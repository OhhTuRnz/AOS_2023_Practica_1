from typing import List, Optional
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import crud, models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
@app.get("/", response_model=List[schemas.Notificacion])
def index(db: Session = Depends(get_db)):
    return crud.get_notificaciones(db)
"""


@app.get("/api/v1/notificaciones", response_model=List[schemas.Notificacion])
def get_notificaciones(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return crud.get_notificaciones(db)

@app.options("/api/v1/notificaciones")
def options_notificacion():
    return "'allow' : {GET, POST, OPTIONS}"

@app.post("/api/v1/notificaciones", response_model=schemas.Notificacion)
def create_notificacion(notificacion: schemas.NotificacionCreate, db: Session = Depends(get_db)):
    print ("main: crea notificacion")
    q = notificacion.dict()
    q.update({"id": "1234-1235"})
    n = schemas.Notificacion.parse_obj(q)
    return crud.create_notificacion(db, n, id=notificacion.id_trabajo)

@app.get("/api/v1/notificaciones/{notificacion_id}")
def get_notificacion_by_id(notificacion_id: str, db: Session = Depends(get_db)):
    return crud.get_notificacion_by_id(db, id=notificacion_id)

@app.options("/api/v1/notificaciones/{notificacion_id}")
def options_notificacion_id():
    return "'allow' : {GET, DELETE, OPTIONS}"

@app.delete("/api/v1/notificaciones/{id_notificacion}")
def delete_notificacion(id_notificacion: str, db: Session = Depends(get_db)):
    return crud.delete_notificacion(db, id_notificacion)

@app.get("/api/v1/notificaciones/trabajo/{id_trabajo}")
def get_notificaciones_by_id_trabajo(id_trabajo: str, db: Session = Depends(get_db)):
    return crud.get_notificaciones_by_id_trabajo(db, id_trabajo=id_trabajo)

@app.options("/api/v1/notificaciones/trabajo/{id_trabajo}")
def options_notificacion_trabajo():
    return "'allow' : {GET, OPTIONS}"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port="8000")