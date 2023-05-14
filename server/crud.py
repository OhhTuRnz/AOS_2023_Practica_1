from http.client import HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from sqlalchemy.orm.exc import NoResultFound
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

def get_notificaciones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Notificacion).offset(skip).limit(limit).all()


def create_notificacion(db: Session, notificacion: schemas.Notificacion, id: str):
    """
    conceptos = notificacion.conceptos
    delattr(notificacion, 'conceptos')
    """
    print ("Creando notificacion")
    db_notificacion = models.Notificacion(**notificacion.dict())
    db.add(db_notificacion)
    """
    for c in conceptos:
        db_concepto = models.NotificacionesConceptos(**c.dict())
        db.add(db_concepto)
    """
    db.commit()
    db.refresh(db_notificacion)
    return db_notificacion


def get_notificacion_by_id(db: Session, id: str):
    try:
        row = db.query(models.Notificacion).filter(models.Notificacion.id == id).one()
    except NoResultFound:
        return None
    return row


def get_notificaciones_by_id_trabajo(db: Session, id_trabajo: str):
    return db.query(models.Notificacion).filter(models.Notificacion.id_trabajo == id_trabajo).all()


def delete_notificacion(db: Session, id: str):
    db.query(models.Notificacion).filter(models.Notificacion.id == id).delete()
    db.commit()
    return 0


"""
def update_notificacion(db: Session, notificacion: schemas.notificacion):
    notificacion = db.query(models.notificacion).filter(models.notificacion.id == notificacion.id).first()
    if notificacion is not None:
        update_notificacion = notificacion.dict(exclude_unset=True)
        db.commit()
        db.refresh()
        return jsonable_encoder(notificacion)
    else:
        return HTTPException()
"""
