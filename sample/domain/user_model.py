from pydantic import BaseModel


class UserTask(BaseModel):
    name: str
