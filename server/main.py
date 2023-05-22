import os

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

import requests
import json
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

from database import SessionLocal, engine
import crud, models, schemas

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from cryptohash import sha256, md5
from utils import generate_jwt, verify_password, get_current_user, get_hashed_password

# Load environment variable file
load_dotenv()

# Init FastAPI
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
        # Enable foreign key constraints
#        db.execute(text("PRAGMA foreign_keys = 1"))
    finally:
        db.close()

@app.post('/login', summary="Create access and refresh tokens for user", response_model=schemas.TokenSchema)
def login(request: Request, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
#async def login(form_data: OAuth2PasswordRequestForm = Depends()):
  # Comprueba el nombre del usuario
  usuario = crud.get_usuario(db, form_data.username)
  if usuario is None:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Incorrect email or password"
    )

  # Comprueba la clave
  hashed_pass = usuario.password
  if not verify_password(form_data.password, hashed_pass):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Incorrect email or password"
    )

  return {
    "access_token": generate_jwt(usuario.nombre, True),
    "refresh_token": generate_jwt(usuario.nombre, False),
    "token_type": "bearer"
  }

def http_get_trabajo(id_trabajo):
    try:
        URL = os.environ["URL_trabajos"] + "/trabajos/" + id_trabajo
        headers = {"authorization": "Bearer " + os.environ["URL_trabajos"]}
        print("Consulta trabajo con: " + URL)
        result = requests.get(URL, headers=headers)
        id_trabajo = str(json.loads(requests.get(URL).text)['idTrabajo'])
    except Exception as e:
        print (e)
    return id_trabajo

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

@app.get("/notificaciones", response_model=schemas.NotificacionesResp)
def get_notificaciones(request: Request, response: Response, db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    global notificaciones

    # Valida credenciales del usuario recibidas en la cabecera HTTP "Authorization: Bearer"
    usuario = get_current_user(db, request)

    url = str(request.url)
    urlBase = url.rsplit("/notificaciones", 1)[0] + "/notificaciones"
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
    result = get_notificaciones_pagina(notificaciones, pag, url, 50) # Page size es 50
    # Añade etag: Firma MD5 de la respuesta
    response.headers['etag'] = md5(result.json())
    return result

@app.post("/notificaciones", response_model=schemas.NotificacionResp)
def create_notificacion(request: Request, response: Response, notificacion: schemas.NotificacionCreate, db: Session = Depends(get_db)):
    # Valida credenciales del usuario recibidas en la cabecera HTTP "Authorization: Bearer"
    usuario = get_current_user(db, request)

    # Consulta el trabajo usando el API de trabajos
    try:
        result = http_get_trabajo(notificacion.id_trabajo)
        if (result != notificacion.id_trabajo):
            raise HTTPException(status_code=422,
                                detail="UNPROCESSABLE ENTITY: Falta alguno de los atributos obligatorios o son incorrectos.'Error de integridad: identificador de trabajo no existe")
    except Exception as exc:
        print ("Error consultando el API de trabajos")

    urlBase = str(request.url).rsplit("/notificaciones", 1)[0] + "/notificaciones"
    response.status_code = 201
    result = addParentSelf(crud.create_notificacion(db, notificacion, id=notificacion.id_trabajo), urlBase)
    # Añade etag: Firma MD5 de la respuesta
    response.headers['etag'] = md5(result.json())
    return result

@app.options("/notificaciones")
def options_notificacion(response: Response):
    response.status_code = 204
    response.headers['allow'] = 'GET, POST, OPTIONS'
    return None

@app.get("/notificaciones/{notificacion_id}")
def get_notificacion_by_id(request: Request, response: Response, notificacion_id: str, db: Session = Depends(get_db)):
    # Valida credenciales del usuario recibidas en la cabecera HTTP "Authorization: Bearer"
    usuario = get_current_user(db, request)

    urlBase = str(request.url).rsplit("/notificaciones", 1)[0] + "/notificaciones"
    result = addParentSelf(crud.get_notificacion_by_id(db, id=notificacion_id), urlBase)
    # Añade etag: Firma MD5 de la respuesta
    response.headers['etag'] = md5(result.json())
    return result

@app.options("/notificaciones/{notificacion_id}")
def options_notificacion_id(response: Response):
    response.status_code = 204
    response.headers['allow'] = 'GET, DELETE, OPTIONS'
    return None

@app.delete("/notificaciones/{id_notificacion}")
def delete_notificacion(request: Request, response: Response, id_notificacion: str, db: Session = Depends(get_db)):
    # Valida credenciales del usuario recibidas en la cabecera HTTP "Authorization: Bearer"
    usuario = get_current_user(db, request)

    response.status_code = 204
    return crud.delete_notificacion(db, id_notificacion)

""" Esta operación la implementa otro grupo """
"""
@app.get("/notificaciones/trabajo/{id_trabajo}")
def get_notificaciones_by_id_trabajo(response: Response, id_trabajo: str, db: Session = Depends(get_db)):
    return crud.get_notificaciones_by_id_trabajo(db, id_trabajo=id_trabajo)
"""

@app.options("/notificaciones/trabajo/{id_trabajo}")
def options_notificacion_trabajo(response: Response):
    response.status_code = 204
    response.headers['allow'] = 'GET, OPTIONS'
    return None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)