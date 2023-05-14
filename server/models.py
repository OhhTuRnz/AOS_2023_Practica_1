from datetime import date

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

#from .database import Base
from database import Base


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