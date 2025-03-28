from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import resume,auth,feedback
from app.core.config import settings
from app.services.firebase_service import initialize_firebase

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name}!"}

app.include_router(feedback.router, prefix="/api/v1")
app.include_router(resume.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

# Run the app (optional, for development)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)