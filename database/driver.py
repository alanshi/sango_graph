from neo4j import AsyncGraphDatabase
from .config import settings

class Neo4jDriver:
    def __init__(self):
        self._driver = None

    async def connect(self):
        self._driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )

    async def close(self):
        if self._driver:
            await self._driver.close()

    @property
    def driver(self):
        if not self._driver:
            raise RuntimeError("Driver not initialized")
        return self._driver

# 初始化驱动实例
driver = Neo4jDriver()

async def get_db():
    # 正确使用异步上下文管理器
    async with driver.driver.session() as session:
        yield session