from datetime import date
import string
from tokenize import String
from typing import List, Optional

from pydantic import BaseModel


class NotificacionBase (BaseModel):
    id_trabajo: str
    estado: str
    detalle: Optional[str] = None
    fecha_emision: Optional[str] = None


class NotificacionCreate (NotificacionBase):
    pass

class Notificacion (NotificacionBase):
    id: str

    class Config:
        orm_mode = True