import os
import traceback

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

import requests
import json
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

from database import SessionLocal, engine
import crud, models, schemas

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from cryptohash import sha256, md5
from utils import generate_jwt, verify_password, get_current_user, get_hashed_password

from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import sessionmaker

import shutil
import os.path

# Load environment variable file
load_dotenv()

if "DEBUG" in os.environ:
    if os.environ["DEBUG"] != "0":
        DEBUG = True
else:
    DEBUG = False

if "SQLALCHEMY_DATABASE_URI" in os.environ:
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
else:
    SQLALCHEMY_DATABASE_URI = "sqlite:///./notificaciones.db"
if DEBUG:
    print ("Cadena de conexión a la base de datos: " + SQLALCHEMY_DATABASE_URI)

# Inicia el fichero de base de datos si no existe
dbFilename = SQLALCHEMY_DATABASE_URI.rsplit("sqlite:///", 1)[1]
if not (os.path.isfile(dbFilename)):
    os.makedirs(os.path.dirname(dbFilename), exist_ok=True)
    shutil.copy("notificaciones.db", dbFilename)

# Inicia sesión con la bse de datos
engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Crea modelos
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()
if "JOURNAL_MODE" in os.environ:
    if DEBUG:
        print ("PRAGMA journal_mode = " + os.environ["JOURNAL_MODE"])
    db.execute(text("PRAGMA journal_mode = " + os.environ["JOURNAL_MODE"]))

# Disabble foreign key constraints
db.execute(text("PRAGMA foreign_keys = OFF"))

# Init FastAPI
app = FastAPI()

# Añade soporte para CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if "URL_TRABAJOS" in os.environ:
    URL_TRABAJOS = os.environ["URL_TRABAJOS"]
else:
    URL_TRABAJOS = "http://localhost:4010"
if DEBUG:
    print ("URL_TRABAJOS: " + URL_TRABAJOS)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
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
        valor = int(id_trabajo)
    except:
        if DEBUG:
            print("El identificador de trabajo debe ser numérico " + id_trabajo)
        raise HTTPException(status_code=422,
                                detail="UNPROCESSABLE ENTITY: Falta alguno de los atributos obligatorios o son incorrectos")
    try:
        URL = URL_TRABAJOS + "/trabajos/" + id_trabajo
        if DEBUG:
            print("Consulta trabajo con: " + URL)

        # Ignoramos el envío de token JWT de autorización a la interfaz de Trabajos
        # headers = {"authorization": "Bearer "}
        headers = {}
        result = requests.get(URL, headers=headers)

        a = json.loads(requests.get(URL).text)
        result = str(json.loads(requests.get(URL).text)['idTrabajo'])
        return result

    except Exception as e:
        if DEBUG:
            print ("Error de consulta al servicio de trabajos")
        raise HTTPException(status_code=500,
                            detail="Error de consulta al servicio de Trabajos")

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
    parameters = parse_qs(urlparse(url).query)
    pag = 1
    order = None
    ordering = None
    if "page" in parameters.keys():
        try:
            pag = int(parameters["page"][0])
        except Exception as e:
            pag = 1
    if "order" in parameters.keys():
        order = parameters["order"][0].lower()
    if "ordering" in parameters.keys():
        ordering = parameters["ordering"][0].upper()

    # Default page size is 100
    page_size = 100
    urlBase = url.rsplit("/notificaciones", 1)[0] + "/notificaciones"
    notificaciones = crud.get_notificaciones(db, order, ordering, (pag-1)*page_size, page_size)
    notificaciones = [addParentSelf(notificacion, urlBase) for notificacion in notificaciones]

    url = url.rsplit("?", 1)[0]
    result = get_notificaciones_pagina(notificaciones, pag, url, page_size)

    # Añade etag: Firma MD5 de la respuesta
    response.headers['etag'] = md5(result.json())
    return result

@app.post("/notificaciones", response_model=schemas.NotificacionResp)
def create_notificacion(request: Request, response: Response, notificacion: schemas.NotificacionCreate, db: Session = Depends(get_db)):
    # Valida credenciales del usuario recibidas en la cabecera HTTP "Authorization: Bearer"
    usuario = get_current_user(db, request)

    # Consulta el trabajo usando el API de trabajos
    result = http_get_trabajo(notificacion.id_trabajo)
    if (result != notificacion.id_trabajo):
        if DEBUG:
            print ("Error de consulta al servicio de trabajos: " + notificacion.id_trabajo)
        raise HTTPException(status_code=422,
                                detail="UNPROCESSABLE ENTITY: Identificador de trabajo no existe")

    urlBase = str(request.url).rsplit("/notificaciones", 1)[0] + "/notificaciones"
    response.status_code = 201
    result = addParentSelf(crud.create_notificacion(db, notificacion, id=notificacion.id_trabajo), urlBase)
    # Añade etag: Firma MD5 de la respuesta
    response.headers['etag'] = md5(result.json())
    return result

@app.options("/notificaciones")
def options_notificacion(request: Request, response: Response):
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
def options_notificacion_id(request: Request, response: Response):
    response.status_code = 204
    response.headers['allow'] = 'GET, DELETE, OPTIONS'
    return None

@app.delete("/notificaciones/{id_notificacion}")
def delete_notificacion(request: Request, response: Response, id_notificacion: str, db: Session = Depends(get_db)):
    # Valida credenciales del usuario recibidas en la cabecera HTTP "Authorization: Bearer"
    usuario = get_current_user(db, request)

    response.status_code = 204
    result = crud.delete_notificacion(db, id_notificacion)
    return result

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
    uvicorn.run(app, host="0.0.0.0", port=4010)