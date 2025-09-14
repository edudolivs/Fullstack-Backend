from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel

from sqllite import run_sql

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_sql(
        """
        CREATE TABLE IF NOT EXISTS users (
            id_users            INTEGER PRIMARY KEY,
            password_users      VARCHAR(255) NOT NULL,
            name_users          VARCHAR(255) NOT NULL,
            email_users         VARCHAR(255) NOT NULL
        )
        """
    )
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

class User(BaseModel):
    password_users: str
    name_users: str
    email_users: str

@router.get("/")
def get_users():
    return run_sql("SELECT * FROM users")

@router.post("/users")
def create_users(body: User):
    password_users, name_users, email_users = body.password_users, body.name_users, body.email_users

    return run_sql(
        f"""
            INSERT INTO users(password_users, name_users, email_users) 
            VALUES('{password_users}', '{name_users}', '{email_users}')
        """
    )

@router.get("/users/{id_users}")
def get_id_user(id_users: int):
    res = run_sql(
        f"""
            SELECT name_users, email_users FROM users WHERE id_users={id_users}
        """
    )
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
            'name_users': res[0][0],
            'email_users': res[0][1]
            }

@router.put("/users/{id_users}")
def update_users(id_users: int, body: User):
    return run_sql(
        f"""
            UPDATE users
            SET
            name_users='{body.name_users}',
            email_users='{body.email_users}',
            password_users='{body.password_users}'
            WHERE id_users={id_users}
        """
    )

class User_Patch(BaseModel):
    column: str
    content: str

@router.patch("/users/{id_users}")
def patch_users(id_users: int, body: User_Patch):
    return run_sql(
        f"""
            UPDATE users
            SET {body.column}='{body.content}'
            WHERE id_users={id_users}
        """
    )

@router.delete("/users/{id_users}")
def delete_users(id_users: int):
    return run_sql(
            f"""
            DELETE FROM users
            WHERE id_users={id_users}
        """
    )

app.include_router(router=router)
