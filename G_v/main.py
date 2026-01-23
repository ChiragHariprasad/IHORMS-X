"""
IHORMS Main Application
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import time

from config import settings
from database import engine
from models import Base
from routers import (
    auth, super_admin, org_admin, branch_admin, 
    doctor, nurse, receptionist, pharmacy, patient_portal,
    billing
)

# Initialize database
# Base.metadata.create_all(bind=engine) # Handled by migration or populator in this case

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(super_admin.router)
app.include_router(org_admin.router)
app.include_router(branch_admin.router)
app.include_router(doctor.router)
app.include_router(nurse.router)
app.include_router(receptionist.router)
app.include_router(pharmacy.router)
app.include_router(patient_portal.router)
app.include_router(billing.router)

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
