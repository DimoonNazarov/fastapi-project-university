from fastapi import FastAPI
import uvicorn
from fastapi.routing import APIRouter
from sqlalchemy import Column, Boolean, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_session
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID
import settings
import uuid
import re
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, validator

#create async engine for interaction with database
#echo=True -логирование всех sql запросов в консоль
engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)


#expire_on_commit=False: Этот параметр указывает, что объекты, загруженные из базы данных
# не должны истекать (или "выходить из строя") после коммита транзакции
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


#       BLOCK WITH DATABASE MODELS


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)


#БЛОК ДЛЯ ВЗАИМОДЕЙСТВИЯ С БАЗОЙ ДАННЫХ YB В БИЗНЕС-КОНТЕКСТЕ


class UserDAL:
    #Data Access Layer for operating user info
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, name:str, surname:str, email:str) -> User:
        new_user = User(name=name, surname=surname, email=email)
        self.db_session.add(new_user)

        #Метод flush() отправляет все изменения, сделанные в текущей сессии, в базу данных
        # flush() не завершает транзакцию
        await self.db_session.flush()
        return new_user




#BLOCK WITH API MODELS

LETTER_MATCH_PARRENT = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")

class TunedModel(BaseModel):
    class Config:
        """tels pydantic to convert even non dict object to json"""
        orm_mode = True


class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool


class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr

    @validator('name')
    def validate_name(cls, value):
        if not LETTER_MATCH_PARRENT.match(value):
            raise HTTPException(status_code=422, detail="Name should contain only letters")
        return value

    @validator('surname')
    def validate_surname(cls, value):
        if not LETTER_MATCH_PARRENT.match(value):
            raise HTTPException(status_code=422, detail="Name should contain only letters")
        return value



#BLOCK WITH API ROUTES
app = FastAPI(title="oxford_university")

user_router = APIRouter()


async def _create_new_user(body: UserCreate) ->ShowUser:
    async with async_session() as session:
        async with session.begin():
            user_dal = UserDAL(db_session=session)
            user = await user_dal.create_user(
                name=body.name,
                surname=body.surname,
                email=body.email
            )
            return ShowUser(
                user_id=user.user_id,
                name=body.name,
                surname=body.surname,
                email=body.email,
                is_active = user.is_active
            )

@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate) -> ShowUser:
    return await _create_new_user(body)


#create the instance for the routes
main_api_router = APIRouter()

main_api_router.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)