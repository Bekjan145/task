from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError

from app.admin.setup import setup_admin
from app.api.v1 import auth_router, user_router, otp_router
from app.db.database import Base, engine

app = FastAPI(title="OTP & JWT Auth API", version="1.0.0")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(otp_router)
app.include_router(user_router)

setup_admin(app)


@app.exception_handler(RedisError)
async def redis_exception_handler(request: Request, exc: RedisError):
    return JSONResponse(status_code=503, content={"detail": "Service temporarily unavailable"})
