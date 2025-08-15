from pydantic import BaseModel



class UsersCreateSchema(BaseModel): # TODO Переименовать
    id: int
    username: str
    first_name: str | None = None
    last_name: str | None = None


    class Config:
        from_attributes = True

