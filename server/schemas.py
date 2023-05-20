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

class Id_Trabajo_Seq (BaseModel):
    id: int

    class Config:
        orm_mode = True

class LinkPag (BaseModel):
    href: str
    rel: str

class LinkPrevNextPag (BaseModel):
    prevPage: LinkPag
    nextPage: LinkPag

class LinkParentSelf (BaseModel):
    parent: LinkPag
    self: LinkPag

class NotificacionConEnlaces(Notificacion):
    links: LinkParentSelf

class NotificacionResp (BaseModel):
    notificacion: NotificacionConEnlaces

class NotificacionesResp (BaseModel):
    notificaciones: List[NotificacionResp]
    links: LinkPrevNextPag

class TokenSchema (BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload (BaseModel):
    iss: str
    aud: str
    sub: str
    exp: int
    iat: int

class Usuario (BaseModel):
    username: str
    password: str
