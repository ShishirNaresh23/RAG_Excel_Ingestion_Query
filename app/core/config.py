from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    llm_model: str = "gpt-4.1-mini"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""

    # App
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()


# import os
# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     # OpenAI
#     openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
#     embedding_model: str = "text-embedding-3-small"
#     embedding_dim: int = 1536
#     llm_model: str = "gpt-4.1-mini"

#     # Qdrant
#     qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
#     qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")

#     # App
#     log_level: str = os.getenv("LOGLEVEL", "INFO") #"INFO"

#     class Config:
#         env_file = ".env"

# settings = Settings()