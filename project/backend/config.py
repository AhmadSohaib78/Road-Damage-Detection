"""
Backend Configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    
    # Model
    model_path: Optional[str] = None
    model_name: str = "yolov8n"
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    
    # Paths
    data_yaml_path: str = "outputs/yolo_dataset/data.yaml"
    dataset_base_path: str = "dataset/data"
    
    # Compute
    device: str = "cpu"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # Frontend
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
