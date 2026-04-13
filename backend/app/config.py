from pydantic import BaseModel
import os

class Settings(BaseModel):
    env: str = os.getenv("ENV", "dev")
    project_name: str = os.getenv("PROJECT_NAME", "learnai")

    # Auth
    auth_mode: str = os.getenv("AUTH_MODE", "noauth")  # noauth|jwt|oauth
    jwt_secret: str = os.getenv("JWT_SECRET", "change_me")

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./storage/app.db")

    # Providers
    model_provider: str = os.getenv("MODEL_PROVIDER", "ollama")  # ollama|openai
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    visible_models: str = os.getenv("VISIBLE_MODELS", "")  # comma separated, empty = show all

    # OAuth
    enable_oauth: bool = os.getenv("ENABLE_OAUTH", "false").lower() == "true"
    oauth_jwt_exp_min: int = int(os.getenv("OAUTH_JWT_EXP_MIN", "10080"))
    google_client_id: str | None = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: str | None = os.getenv("GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str | None = os.getenv("GOOGLE_REDIRECT_URI")
    github_client_id: str | None = os.getenv("GITHUB_CLIENT_ID")
    github_client_secret: str | None = os.getenv("GITHUB_CLIENT_SECRET")
    github_redirect_uri: str | None = os.getenv("GITHUB_REDIRECT_URI")

settings = Settings()
