from contextlib import asynccontextmanager
from fastapi import FastAPI
from database.driver import driver
from routers import people


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles



# You can add additional URLs to this list, for example, the frontend's production domain, or other frontends.



@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化阶段
    try:
        await driver.connect()
        yield
    finally:
        # 清理阶段
        await driver.close()
        if hasattr(driver, "metrics"):
            print(f"Connection metrics: {driver.get_metrics()}")  # 输出连接指标

app = FastAPI(lifespan=lifespan)
app.include_router(people.router)

origins = [
    "*",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源（生产环境建议指定具体域名）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)