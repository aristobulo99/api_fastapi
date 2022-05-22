from datetime import timedelta, datetime
from os import access
from click import password_option
from fastapi import APIRouter, status,Response, Depends, HTTPException
from bson import ObjectId
from passlib.hash import sha256_crypt
from starlette.status import HTTP_204_NO_CONTENT

from models.user import User
from config.db import conn
from schemas.user import userEntity, usersEntity
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import re
SECRET_KEY = '0a6e380769dd781432fa40ac333221a2fa729ded07d9639431666322c8efd017'
ALGORITHM = "HS256"
regex = '^[a-z0-9]+[a-z0-9]+[@]\w+[.]\w{2,3}$'

def check(email):  
    if(re.search(regex,email)):  
        return True  
    else:  
        return False

user = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class user_logi():
    username: str
    password: str

def autenticar_user(username, password):
    bus = conn.aplicacion.datos.find_one({"correo": username}) 
    if bus == None:
        user = False
    else:
        user = True  
    if user: 
        password_check = sha256_crypt.verify(password, bus["password"])
        return password_check
    else:
        False

def create_access_token(data:  dict, expire: timedelta):
    to_encode = data.copy()
    exp = datetime.utcnow() + expire
    to_encode.update({"exp": exp})
    encode_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt

@user.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_logi.username = form_data.username
    user_logi.password = form_data.password

    if autenticar_user(user_logi.username, user_logi.password):
        bus = conn.aplicacion.datos.find_one({"correo": user_logi.username}) 
        access_token = create_access_token(
            data={"sub":user_logi.username}, expire=timedelta(minutes=2)
        )
        return {"access_token": access_token, "token_type":"bearer"}
    else:
        raise HTTPException(status_code=400, detail="Incorrect Username or Password")

@user.get('/users2', tags=["users"])
def find_all_users2(token: str = Depends(oauth2_scheme)):
    #print(list(conn.data_flutter.datos.find()))
    return{"token": token}
    #return usersEntity(conn.data_flutter.datos.find())

@user.get('/users', response_model=list[User], tags=["users"])
async def find_all_users(token: str = Depends(oauth2_scheme)):
    #print(list(conn.data_flutter.datos.find()))
    return usersEntity(conn.aplicacion.datos.find())


@user.post('/users', response_model=User, tags=["users"])
async def create_user(user: User):
    new_user = dict(user)
    veri = check(new_user["correo"])
    buscar = conn.aplicacion.datos.find_one({"correo": new_user["correo"]})
    if buscar == None:
        if(veri):
            new_user["password"] = sha256_crypt.encrypt(new_user["password"])
            del new_user["id"]
            id = conn.aplicacion.datos.insert_one(new_user).inserted_id
            user = conn.aplicacion.datos.find_one({"_id": id})
            return userEntity(user)
        else:
            return Response("El correo no es valido")
    else:
        return Response("El correo ya existe, ingrese otro por favor")


@user.get('/users/{id}', response_model=User, tags=["users"])
async def find_user(token: str = Depends(oauth2_scheme)):
    return userEntity(conn.aplicacion.datos.find_one({"correo":user_logi.username}))


@user.put("/users/{id}", response_model=User, tags=["users"])
async def update_user(user: User,token: str = Depends(oauth2_scheme)):
    new_user = dict(user)
    new_user["password"] = sha256_crypt.encrypt(new_user["password"])
    buscar = conn.aplicacion.datos.find_one({"correo": new_user["correo"]})
    if buscar == None:
        conn.aplicacion.datos.find_one_and_update({
            "correo": user_logi.username
        }, {
            "$set": dict(new_user)
        })
        return userEntity(conn.aplicacion.datos.find_one({"correo": new_user["correo"]}))
    else:
        return Response("El correo ya existe, ingrese otro por favor")


@user.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
async def delete_user(token: str = Depends(oauth2_scheme)):
    conn.aplicacion.datos.find_one_and_delete({
        "correo": user_logi.username
    })
    return Response(status_code=HTTP_204_NO_CONTENT)
