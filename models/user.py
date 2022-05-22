from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: Optional[str]
    nombre: str
    apellido: str
    sexo: str
    correo: str
    password: str