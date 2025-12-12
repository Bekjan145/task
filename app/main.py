from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers import auth, otp, user

app = FastAPI(title="OTP & JWT Auth API", version="1.0.0")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(otp.router)
app.include_router(user.router)
