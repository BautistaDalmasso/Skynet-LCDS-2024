from pydantic import BaseModel


class CreateUserDTO(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str


class LoginDTO(BaseModel):
    email: str
    password: str


class CheckChallengeDTO(BaseModel):
    email: str
    deviceUID: int
    challenge: list[int]


class UpdateRSADTO(BaseModel):
    publicRSA: str
    deviceUID: int


class UpdateUserDniDTO(BaseModel):
    dni: str