from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "admin123456"

    # 新配置方式（替代原来的 class Config）
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


settings = Settings()