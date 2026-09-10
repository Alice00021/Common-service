from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List


def setup_cors(
    app: FastAPI,
    origins: List[str],
    allow_credentials: bool = True,
    allow_methods: List[str] = None,
    allow_headers: List[str] = None
) -> None:
    """Настроить CORS"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods or ["*"],
        allow_headers=allow_headers or ["*"],
    )