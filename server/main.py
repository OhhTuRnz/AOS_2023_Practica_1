from typing import List, Optional
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import crud, models, schemas

from sqlalchemy import create_engine, text

from urllib.parse import urlparse
from urllib.parse import parse_qs

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.execute(text("PRAGMA foreign_keys = 1")) # Enable foreign key constraints
    finally:
        db.close()

"""
@app.get("/", response_model=List[schemas.Notificacion])
def index(db: Session = Depends(get_db)):
    return crud.get_notificaciones(db)
"""

def addParentSelf(notificacion, urlBase):
    parent = schemas.LinkPag(href=urlBase, rel="notificacion_post notificacion_cget")
    self = schemas.LinkPag(href=urlBase+"/"+str(notificacion.id), rel="notificacion_get")
    links = schemas.LinkParentSelf(parent=parent, self=self)
    notificacion = schemas.NotificacionConEnlaces(id=notificacion.id,
        id_trabajo=notificacion.id_trabajo, estado=notificacion.estado,
        detalle=notificacion.detalle, fecha_emision=notificacion.fecha_emision,
        links=links)
    return schemas.NotificacionResp(notificacion=notificacion)

def get_notificaciones_pagina(notificaciones, pag, url, size):
    maxPag = int((len(notificaciones)-1) / size) + 1
    pag = 1 if pag < 1 else (maxPag if pag > maxPag else pag)

    prev = 1 if pag == 1 else pag-1
    next = pag if (pag+1) * size > len(notificaciones) else pag + 1
    prevPage = schemas.LinkPag(href=url+"?page="+str(prev), rel="prevPage")
    nextPage = schemas.LinkPag(href=url+"?page="+str(next), rel="nextPage")
    links = schemas.LinkPrevNextPag(prevPage=prevPage, nextPage=nextPage)

    subconjunto = []
    if (len(notificaciones) > 0):
        start = (pag - 1) * size
        stop = pag * size
        if (stop >= len(notificaciones)):
            stop = len(notificaciones)
        indices = range(start, stop)
        subconjunto = [notificaciones[i] for i in indices]
    result = schemas.NotificacionesResp(notificaciones=subconjunto, links=links)
    return result

@app.get("/api/v1/notificaciones", response_model=schemas.NotificacionesResp)
def get_notificaciones(request: Request, db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    global notificaciones

    # Simula usuario no autorizado
    if "usuario" in request.headers.keys():
        raise HTTPException(status_code=401, detail="La solicitud requiere autenticación y el usuario no está autorizado para acceder al recurso.")

    url = str(request.url)
    urlBase = url.rsplit("/api/v1/notificaciones", 1)[0] + "/api/v1/notificaciones"
    parameters = parse_qs(urlparse(url).query)
    if "page" in parameters.keys():
        try:
            pag = int(parameters["page"][0])
        except Exception as e:
            pag = 1
    else:
        notificaciones = crud.get_notificaciones(db)
        notificaciones = [addParentSelf(notificacion, urlBase) for notificacion in notificaciones]
        pag = 1
    url = url.rsplit("?", 1)[0]
    return get_notificaciones_pagina(notificaciones, pag, url, 2)

@app.post("/api/v1/notificaciones", response_model=schemas.NotificacionResp)
def create_notificacion(request: Request, response: Response, notificacion: schemas.NotificacionCreate, db: Session = Depends(get_db)):
    urlBase = str(request.url).rsplit("/api/v1/notificaciones", 1)[0] + "/api/v1/notificaciones"
    response.status_code = 201
    return addParentSelf(crud.create_notificacion(db, notificacion, id=notificacion.id_trabajo), urlBase)

@app.options("/api/v1/notificaciones")
def options_notificacion(response: Response):
    response.status_code = 204
    response.headers['allow'] = 'GET, POST, OPTIONS'
    return None

@app.get("/api/v1/notificaciones/{notificacion_id}")
def get_notificacion_by_id(request: Request, response: Response, notificacion_id: str, db: Session = Depends(get_db)):
    # Simula usuario no autorizado
    if "usuario" in request.headers.keys():
        raise HTTPException(status_code=401, detail="La solicitud requiere autenticación y el usuario no está autorizado para acceder al recurso.")

    urlBase = str(request.url).rsplit("/api/v1/notificaciones", 1)[0] + "/api/v1/notificaciones"
    return addParentSelf(crud.get_notificacion_by_id(db, id=notificacion_id), urlBase)

@app.options("/api/v1/notificaciones/{notificacion_id}")
def options_notificacion_id(response: Response):
    response.status_code = 204
    response.headers['allow'] = 'GET, DELETE, OPTIONS'
    return None

@app.delete("/api/v1/notificaciones/{id_notificacion}")
def delete_notificacion(response: Response, id_notificacion: str, db: Session = Depends(get_db)):
    response.status_code = 204
    return crud.delete_notificacion(db, id_notificacion)

""" Esta operación la implementa otro grupo """
"""
@app.get("/api/v1/notificaciones/trabajo/{id_trabajo}")
def get_notificaciones_by_id_trabajo(response: Response, id_trabajo: str, db: Session = Depends(get_db)):
    return crud.get_notificaciones_by_id_trabajo(db, id_trabajo=id_trabajo)
"""

@app.options("/api/v1/notificaciones/trabajo/{id_trabajo}")
def options_notificacion_trabajo(response: Response):
    response.status_code = 204
    response.headers['allow'] = 'GET, OPTIONS'
    return None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port="8000")