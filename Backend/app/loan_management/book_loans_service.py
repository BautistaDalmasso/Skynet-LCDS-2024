from datetime import datetime
from enum import auto
import json
import sqlite3
from app.models import auto_index
from app.catalogue.browse_catalogue_service import BrowseCatalogueService
from .book_loans_dtos import (
    LOAN_STATUS,
    PCDI,
    ReservationRequestDTO,
    LoanInformationDTO,
    PhysicalCopyDTO,
    LoanValidationDTO,
)

from pathlib import Path
from app.database.database_user import DatabaseUser
from typing import List
from typing import Any


class BookNotFound(Exception):
    pass


class NoCopiesAvailable(Exception):
    pass


class BookAlreadyReturned(Exception):
    pass


class UnkwnownFilter(Exception): ...


class LoanService(DatabaseUser):
    def __init__(self, db_path: Path, catalogue_path: Path) -> None:
        super().__init__(db_path)
        self._catalogue_service = BrowseCatalogueService(catalogue_path)

    def reserve_book(self, book_request: ReservationRequestDTO) -> LoanInformationDTO:
        """Mark a copy of a book as reserved.."""
        copy_data = self._find_available_copy_data(book_request.isbn)
        catalogue_data = self._catalogue_service.browse_by_isbn(book_request.isbn)

        loan_status: LOAN_STATUS = "reserved"
        today = datetime.today()

        loan_information = LoanInformationDTO(
            inventory_number=copy_data.inventoryNumber,
            catalogue_data=catalogue_data,
            expiration_date=book_request.expiration_date,
            user_email=book_request.user_email,
            loan_status=loan_status,
            reservation_date=today,
            checkout_date=None,
            return_date=None,
        )

        self.execute_in_database(
            """INSERT INTO loan (inventoryNumber, expirationDate, userEmail, loanStatus)
                        VALUES (?, ?, ?, ?)""",
            (
                loan_information.inventory_number,
                loan_information.expiration_date,
                loan_information.user_email,
                loan_information.loan_status,
            ),
        )

        return loan_information

    def _find_available_copy_data(self, isbn) -> PhysicalCopyDTO:

        try:
            connection = sqlite3.connect(self._db_path)
            cursor = connection.cursor()

            connection.execute("BEGIN")
            cursor.execute(
                """SELECT * FROM bookInventory
                WHERE isbn = ? AND status = ?""",
                (isbn, "available"),
            )
            data = cursor.fetchone()

            if data is None:
                raise NoCopiesAvailable(
                    f"Libro con isbn: {isbn} no tiene copias disponibles."
                )

            copy_data = PhysicalCopyDTO(
                inventoryNumber=data[PCDI.inventoryNumber.value],
                isbn=data[PCDI.isbn.value],
                status=data[PCDI.status.value],
            )

            cursor.execute(
                """UPDATE bookInventory SET status = ? WHERE inventoryNumber = ?""",
                ("borrowed", copy_data.inventoryNumber),
            )

            connection.commit()

            copy_data.status = "borrowed"
            return copy_data
        except Exception as e:
            connection.rollback()
            print("Transaction rolled back due to error:", e)
            raise e
        finally:
            cursor.close()
            connection.close()

    def consult_book_loans_by_user_email(self, email: str) -> List[LoanInformationDTO]:
        loans = self.query_multiple_rows(
            """SELECT loan.*, bookInventory.isbn
            FROM loan
            INNER JOIN bookInventory ON loan.inventoryNumber = bookInventory.inventoryNumber
            WHERE loan.userEmail = ?""",
            (email,),
        )
        return [self.create_loan_data(entry) for entry in loans]

    def consult_book_loans_by_title(self, title: str) -> List[LoanInformationDTO]:

        loans = self.query_multiple_rows(
            """SELECT loan.*, bookInventory.isbn
            FROM loan
            INNER JOIN bookInventory ON loan.inventoryNumber = bookInventory.inventoryNumber""",
            tuple(),
        )
        query_result: List[LoanInformationDTO] = [
            self.create_loan_data(entry) for entry in loans
        ]
        filtered_result = list(filter(lambda x: x.title == title, query_result))
        return filtered_result

    def consult_all_book_loans(self) -> List[LoanInformationDTO]:

        loans = self.query_multiple_rows(
            """SELECT loan.*, bookInventory.isbn
            FROM loan
            INNER JOIN bookInventory ON loan.inventoryNumber = bookInventory.inventoryNumber""",
            tuple(),
        )
        return [self.create_loan_data(entry) for entry in loans]

    def create_loan_data(self, db_entry: list[Any]) -> LoanInformationDTO:
        catalogue_data = self._catalogue_service.browse_by_isbn(
            db_entry[CLBEI.isbn.value]
        )

        return LoanInformationDTO(
            id=db_entry[CLBEI.id.value],
            catalogue_data=catalogue_data,
            inventory_number=db_entry[CLBEI.inventory_number.value],
            expiration_date=db_entry[CLBEI.expiration_date.value],
            user_email=db_entry[CLBEI.user_email.value],
            loan_status=db_entry[CLBEI.loan_status.value],
            reservation_date=db_entry[CLBEI.reservation_date.value],
            checkout_date=db_entry[CLBEI.checkout_date.value],
            return_date=db_entry[CLBEI.return_date.value],
        )

    def lend_book(self, inventory_number: int, user_email: str) -> LoanInformationDTO:
        loan_status: LOAN_STATUS = "loaned"
        today_str = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.execute_in_database(
                """UPDATE loan
                SET loanStatus = ?, checkoutDate = ?
                WHERE inventoryNumber = ? AND userEmail = ?""",
                (loan_status, today_str, inventory_number, user_email),
            )
            return self.create_lend_book(inventory_number, user_email)
        except sqlite3.IntegrityError:
            return {"error": "No se pudo registrar el prestamo."}

    def create_lend_book(
        self, inventory_number: int, user_email: str
    ) -> LoanInformationDTO:
        loan_status: LOAN_STATUS = "loaned"
        book_isbn = self.query_database(
            """SELECT isbn
                        FROM bookInventory
                        WHERE inventoryNumber = ?""",
            (inventory_number,),
        )
        loaned_book = self.query_database(
            """SELECT *
                FROM loan
                WHERE inventoryNumber = ? AND userEmail = ? AND loanStatus = ?""",
            (inventory_number, user_email, loan_status),
        )
        catalogue_data = self._catalogue_service.browse_by_isbn(book_isbn[0])
        return LoanInformationDTO(
            catalogue_data=catalogue_data,
            inventory_number=loaned_book[1],
            expiration_date=loaned_book[2],
            user_email=loaned_book[3],
            loan_status=loaned_book[4],
            reservation_date=loaned_book[5],
            checkout_date=loaned_book[6],
            return_date=loaned_book[7],
        )

    def check_valid_loan(
        self, inventory_number: int, user_email: str
    ) -> LoanValidationDTO | None:
        book = self.query_database(
            """SELECT inventoryNumber
                FROM loan
                WHERE inventoryNumber = ? AND userEmail = ? AND (loanStatus = returned OR loanStatus = reserved) """,
            (inventory_number, user_email),
        )
        if bool(book):
            return LoanValidationDTO(
                inventory_number=inventory_number,
                user_email=user_email,
            )
        else:
            return None


class CLBEI(auto_index):
    """Consult Loans By Email Indexes"""

    id = auto()
    inventory_number = auto()
    expiration_date = auto()
    user_email = auto()
    loan_status = auto()
    reservation_date = auto()
    checkout_date = auto()
    return_date = auto()
    isbn = auto()
