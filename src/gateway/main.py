"""
API Gateway - единая точка входа для всех микросервисов
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.gateway.router import router_gateway


def create_fast_api_app() -> FastAPI:
    fastapi_app = FastAPI(
        title="API Gateway",
        description="Единая точка входа для микросервисов",
        version="1.0.0"
    )

    fastapi_app.include_router(router_gateway, prefix='/api')

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return fastapi_app

app = create_fast_api_app()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

