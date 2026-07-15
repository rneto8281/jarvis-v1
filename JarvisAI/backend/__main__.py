"""Permite iniciar o JarvisAI com ``python -m backend``."""

from __future__ import annotations

import uvicorn

from backend.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=False,
    )
