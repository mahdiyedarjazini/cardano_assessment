import uvicorn
from fastapi import FastAPI

from trade_app.api.routes import router
from trade_app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="A service for enriching financial transaction data",
    version="1.0.0",
)

app.include_router(router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
