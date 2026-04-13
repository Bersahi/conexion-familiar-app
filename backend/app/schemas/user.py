from pydantic import BaseModel, EmailStr

# Lo que llega al crear usuario
class UserCreate(BaseModel):
    name: str
    email: EmailStr        # valida formato de email automáticamente
    password: str
    role_id: int

# Lo que se devuelve al cliente (sin password)
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role_id: int

    model_config = {"from_attributes": True}