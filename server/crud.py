from http.client import HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from sqlalchemy import exc
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.sql import text
from fastapi import HTTPException

# Carga datos iniciales en la base de datos si aún no han sido cargados
def load_db(db: Session):
    try:
        sql = text('SELECT * FROM id_trabajo_seq')
        result = db.execute(sql).all()
        if len(result) > 0:
            # Los datos ya están cargados
            return
    except Exception as e:
        return

    # Inicia base de datos
    try:
        # Insert numero de secuencia
        sql = text('INSERT INTO id_trabajo_seq VALUES (1)')
        db.execute(sql)

        # Inserta usuario demo
        sql = text('INSERT INTO usuarios VALUES ("demo", "$2b$12$23EsRw/O3CEx/tFYG.FLDu2Ln9C5rZJ5BxpA.jK8kEQf6NHiTfo7e")')
        db.execute(sql)

        # Inserta trabajos "1" y "1234-1234"
        sql = text('INSERT INTO trabajos VALUES ("1")')
        db.execute(sql)
        sql = text('INSERT INTO trabajos VALUES ("1234-1234")')
        db.execute(sql)

        # Inserta notificaciones "1234-1234-12" y "1234-1234-13"
        sql = text('INSERT INTO notificaciones VALUES ("1234-1234-12", "1234-1234", "Creado", "Solicitado por el cliente", "2023-04-05 12:00:58")')
        db.execute(sql)
        sql = text('INSERT INTO notificaciones VALUES ("1234-1234-13", "1234-1234", "Planificado", "Asignado mecánico", "2023-04-05 12:00:58")')
        db.execute(sql)

        db.commit()
    except Exception as e:
        db.rollback()
        print ("Error iniciando la base de datos")
    return

def get_usuario(db: Session, nombre: str):
    try:
        row = db.query(models.Usuario).filter(models.Usuario.nombre == nombre).one()
    except exc.NoResultFound:
        row = None
    return row

def get_notificaciones(db: Session, order, ordering, skip: int = 0, limit: int = 100):
    if order == "id":
        if ordering == "ASC":
            result = db.query(models.Notificacion).order_by(models.Notificacion.id.asc()).offset(skip).limit(limit).all()
        elif ordering == "DESC":
            result = db.query(models.Notificacion).order_by(models.Notificacion.id.desc()).offset(skip).limit(limit).all()
        else:
            result = db.query(models.Notificacion).order_by(models.Notificacion.id).offset(skip).limit(limit).all()
    elif order == "id_trabajo":
        if ordering == "ASC":
            result = db.query(models.Notificacion).order_by(models.Notificacion.id_trabajo.asc()).offset(skip).limit(limit).all()
        elif ordering == "DESC":
            result = db.query(models.Notificacion).order_by(models.Notificacion.id_trabajo.desc()).offset(skip).limit(limit).all()
        else:
            result = db.query(models.Notificacion).order_by(models.Notificacion.id_trabajo).offset(skip).limit(limit).all()
    else:
        result = db.query(models.Notificacion).offset(skip).limit(limit).all()
    return result

def create_notificacion(db: Session, notificacion: schemas.Notificacion, id: str):
    # Comprueba que el valor de estado es uno de los predefinidos
    if not notificacion.estado in ["Creado", "Planificado", "Iniciado", "Anulado", "Terminado"]:
        raise HTTPException(status_code=409,
                            detail="CONFLICT: La petición no ha sido completada debido a un conflicto con el servidor.")

    # Comprueba que exista alguna notificación para ese mismo trabajo con estado "Creado"
    result = get_notificaciones_by_id_trabajo_estado(db, notificacion.id_trabajo, "Creado")
    if notificacion.estado.lower() == "creado":
        if len(result) > 0:
            raise HTTPException(status_code=409,
                                detail="CONFLICT: La petición no ha sido completada debido a un conflicto con el servidor.")
        notificacion.estado = "Creado"
    else:
        if len(result) == 0:
            raise HTTPException(status_code=409, detail="CONFLICT: La petición no ha sido completada debido a un conflicto con el servidor.")

    try:
        id_notificacion = get_next_id_notificacion(db)
        # Añade identificador de la notificación
        q = notificacion.dict()
        q.update({"id": id_notificacion})
        notificacion = schemas.Notificacion.parse_obj(q)
        db_notificacion = models.Notificacion(**notificacion.dict())
        db.add(db_notificacion)
        db.commit()
        db.refresh(db_notificacion)
    except exc.IntegrityError as e:
        raise HTTPException(status_code=422, detail="Error de integridad: " + e.orig.args[0])
    return db_notificacion


def get_notificacion_by_id(db: Session, id: str):
    try:
        row = db.query(models.Notificacion).filter(models.Notificacion.id == id).one()
    except exc.NoResultFound:
        raise HTTPException(status_code=404, detail="Recurso no disponible")
    return row

def get_notificaciones_by_id_trabajo(db: Session, id_trabajo: str):
    return db.query(models.Notificacion).filter(models.Notificacion.id_trabajo == id_trabajo).all()

def get_notificaciones_by_id_trabajo_estado(db: Session, id_trabajo: str, estado: str):
    return db.query(models.Notificacion)\
        .filter(models.Notificacion.id_trabajo == id_trabajo)\
        .filter(models.Notificacion.estado == estado)\
        .all()

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

def get_next_id_notificacion(db: Session):
    sql = text('INSERT INTO id_trabajo_seq values (null)')
    row = db.execute(sql)
    rowid = row.lastrowid
    lowid = rowid % 1000000
    midid = int(rowid/10000)
    highid = int(midid/10000)
    midid -= highid
    id_notificacion = "{:04d}-{:04d}-{:02d}".format(highid, midid, lowid)
    sql = text('DELETE FROM id_trabajo_seq WHERE id = \"' + str(rowid-1) + '"')
    db.execute(sql)
    return id_notificacion