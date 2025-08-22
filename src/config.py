from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings): 
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, strict=True)

    manifest_url: str
    chunk_size: int = 8192
    
        
settings = Settings()