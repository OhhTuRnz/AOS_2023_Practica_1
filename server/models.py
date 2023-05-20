from datetime import date

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

#from .database import Base
from database import Base


class Id_Trabajo_Seq(Base):
    __tablename__ = "id_trabajo_seq"
    id = Column(Integer, primary_key=True, index=True)

class Trabajo(Base):
    __tablename__ = "trabajos"
    id = Column(String, primary_key=True, index=True)

class Notificacion(Base):
    __tablename__ = "notificaciones"
    id = Column(String, primary_key=True, index=True)
    id_trabajo: Mapped[String] = mapped_column(ForeignKey("trabajos.id"))
    estado = Column(String)
    detalle = Column(String)
    fecha_emision = Column(String)

class Usuario(Base):
    __tablename__ = "usuarios"
    nombre = Column(String, primary_key=True, index=True)
    password = Column(String)
