from typing import List, Optional
import os

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

import requests
import json
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

from database import SessionLocal, engine
import crud, models, schemas

from cryptohash import sha256, md5

from authlib.jose import jwt
import time

load_dotenv()


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

# Genera token JWT
#
def generate_jwt():
    # JSON Web Key (JWK) para la clave privada ES256 que se usará en la generación de JWT tokens
    global jwk
    jwk = {
        "crv": "P-256",
        "kty": "EC",
        "alg": "ES256",
        "use": "sig",
        "kid": "a32fdd4b146677719ab2372861bded89",
        "d": "5nYhggWQzfPFMkXb7cX2Qv-Kwpyxot1KFwUJeHsLG_o",
        "x": "-uTmTQCbfm2jcQjwEa4cO7cunz5xmWZWIlzHZODEbwk",
        "y": "MwetqNLq70yDUnw-QxirIYqrL-Bpyfh4Z0vWVs_hWCM"
    }
    header = {"alg": "ES256"}
    payload = {
        "iss": "AOS 2023 - API Notificaciones",  # Issuer
        "aud": "alejandro.carrasco.aragon@alumnos.upm.es",  # Audience
        "sub": "9377717bef5a48c289baa2d242367ca5",  # Subject
        "exp": int(time.time()) + 31536000,  # Expires at time (1 año a partir de la hora actual)
        "iat": int(time.time())  # Issued at time
    }
    return jwt.encode(header, payload, jwk)

def compruebaCredenciales(autenticacion):
    if autenticacion.startswith("Bearer "):
        token = autenticacion.rsplit("Bearer ", 1)[1]
#        claims = jwt.decode(token, jwk)
        print (token)
        print (os.environ["jwt_notificaciones"])
        return token == os.environ["jwt_notificaciones"]
    return true

# Generación de token JWT
# jwt_notificaciones = generate_jwt()
# print(jwt_notificaciones.decode("utf-8"))
jwt_notificaciones = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImEzMmZkZDRiMTQ2Njc3NzE5YWIyMzcyODYxYmRlZDg5In0.eyJpc3MiOiJBT1MgMjAyMyAtIEFQSSBOb3RpZmljYWNpb25lcyIsImF1ZCI6ImFsZWphbmRyby5jYXJyYXNjby5hcmFnb25AYWx1bW5vcy51cG0uZXMiLCJzdWIiOiI5Mzc3NzE3YmVmNWE0OGMyODliYWEyZDI0MjM2N2NhNSIsImV4cCI6MTY4NDUyNDA2MywiaWF0IjoxNjg0NTIzNzYzfQ.TmP_jb4WF_mxl-lAauAFDCKLi-w2agpToTKpL5UbGMwuyn4RlVZdCM3EdNl-RZ1Yl7rfYl5N6KLb01hz1ThJVg";

def http_get_trabajo(id_trabajo):
    try:
        URL = os.environ["URL_trabajos"] + "/trabajos/" + id_trabajo
        headers = {"authorization": "Bearer " + os.environ["jwt_trabajos"]}
        print("Consulta trabajo con: " + URL)
        result = requests.get(URL, headers=headers)
        idTrabajo = str(json.loads(requests.get(URL).text)['idTrabajo'])
    except Exception as e:
        print (e)
    return idTrabajo

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
def get_notificaciones(request: Request, response: Response, db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    global notificaciones

    # Chequea credenciales del usuario
    if "authorization" in request.headers.keys():
        if not compruebaCredenciales(request.headers["authorization"]):
            raise HTTPException(status_code=401, detail="UNAUTHORIZED: Usuario no autorizado.")

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
    result = get_notificaciones_pagina(notificaciones, pag, url, 50) # Page size es 50
    # Añade etag: Firma MD5 de la respuesta
    response.headers['etag'] = md5(result.json())
    return result

@app.post("/api/v1/notificaciones", response_model=schemas.NotificacionResp)
def create_notificacion(request: Request, response: Response, notificacion: schemas.NotificacionCreate, db: Session = Depends(get_db)):
    # Consulta el trabajo usando el API
    found = True
    try:
        result = http_get_trabajo(notificacion.id_trabajo)
        if (result != notificacion.id_trabajo):
            found = False
    except Exception as e:
        found = True

    if not found:
        raise HTTPException(status_code=422, detail="UNPROCESSABLE ENTITY: Falta alguno de los atributos obligatorios o son incorrectos.'Error de integridad: identificador de trabajo no existe")

    urlBase = str(request.url).rsplit("/api/v1/notificaciones", 1)[0] + "/api/v1/notificaciones"
    response.status_code = 201
    result = addParentSelf(crud.create_notificacion(db, notificacion, id=notificacion.id_trabajo), urlBase)
    # Añade etag: Firma MD5 de la respuesta
    response.headers['etag'] = md5(result.json())
    return result

@app.options("/api/v1/notificaciones")
def options_notificacion(response: Response):
    response.status_code = 204
    response.headers['allow'] = 'GET, POST, OPTIONS'
    return None

@app.get("/api/v1/notificaciones/{notificacion_id}")
def get_notificacion_by_id(request: Request, response: Response, notificacion_id: str, db: Session = Depends(get_db)):
    # Simula usuario no autorizado
    if "usuario" in request.headers.keys():
        raise HTTPException(status_code=401, detail="UNAUTHORIZED: Usuario no autorizado.")

    urlBase = str(request.url).rsplit("/api/v1/notificaciones", 1)[0] + "/api/v1/notificaciones"
    result = addParentSelf(crud.get_notificacion_by_id(db, id=notificacion_id), urlBase)
    response.headers['etag'] = md5(result.encode("utf-8")).hexdigest()
    # Añade etag: Firma MD5 de la respuesta
    response.headers['etag'] = md5(result.json())
    return result

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
    uvicorn.run(app, host="0.0.0.0", port=8000)