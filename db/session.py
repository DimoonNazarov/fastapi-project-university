from typing import Generator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import settings





#create async engine for interaction with database
#echo=True -логирование всех sql запросов в консоль
engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)


#expire_on_commit=False: Этот параметр указывает, что объекты, загруженные из базы данных
# не должны истекать (или "выходить из строя") после коммита транзакции
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> Generator:
    """Dependency for getting async session"""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()