# See: https://medium.com/@apcelent/json-web-token-tutorial-with-example-in-python-df7dda73b579
# See: https://www.freecodecamp.org/news/how-to-add-jwt-authentication-in-fastapi/

import os
import time

import jwt
from passlib.context import CryptContext

from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session

import crud
from schemas import TokenPayload
from datetime import datetime
from dotenv import load_dotenv

from time import strftime, localtime

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

def generate_jwt(subject, access) -> str:
    iat = time.time()
    if access:
        exp = iat + ACCESS_TOKEN_EXPIRE_MINUTES * 60
    else:
        exp = iat + REFRESH_TOKEN_EXPIRE_MINUTES * 60
    header = {'alg': 'RS256'}
    payload = {
        "iss": "AOS 2023 - API Notificaciones",  # Issuer
        "aud": "AOS UPM",  # Audience
        "sub": subject,  # Subject
        "exp": exp,  # Expires at time (1 año a partir de la hora actual)
        "iat": iat  # Issued at time
    }
    encoded = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    if access:
        print ("Access Token: " + encoded)
        print ("Access Token expira el " + strftime("%Y-%m-%d %H:%M:%S", localtime(payload['exp'])))
    else:
        print ("Refresh Token: " + encoded)
        print("Refresh Token expira el " + strftime("%Y-%m-%d %H:%M:%S", localtime(payload['exp'])))
    return encoded

def get_current_user(db: Session, request: Request) -> str:

    authorization: str = request.headers.get("Authorization")
    if authorization == None:
        return None
    scheme, token = get_authorization_scheme_param(authorization)
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], audience="AOS UPM")
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Signature has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as exc:
        payload = jwt.decode(token, options={"verify_signature": False})
        print ("Token expiro el: " + strftime("%Y-%m-%d %H:%M:%S"), localtime(payload['exp']))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = crud.get_usuario(db, token_data.sub)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario