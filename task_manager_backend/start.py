#!/usr/bin/env python3
"""
FastAPI Task Manager Backend Startup Script

This script starts the FastAPI application with proper configuration.
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Configure uvicorn based on environment
    if environment == "development":
        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    else:
        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=port,
            reload=False,
            log_level="warning"
        )
