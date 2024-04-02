from pydantic import BaseModel


class CreateUser(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str


class LoginDTO(BaseModel):
    email: str
    password: str


class CheckChallengeDTO(BaseModel):
    email: str
    challenge: list[int]


class UpdateRSADTO(BaseModel):
    publicRSA: str
