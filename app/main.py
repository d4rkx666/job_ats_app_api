from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import resume,auth,feedback, profile, export
from app.core.config import settings
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from app.services.user_actions_manager import reset_monthly_credits

# Initialize scheduler at module level (outside FastAPI app)
scheduler = BackgroundScheduler()
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler.add_job(
        reset_monthly_credits,
        'cron',
        hour=0,
        minute=1,
        timezone='UTC'
    )
    scheduler.start()
    
    yield
    
    # Shutdown
    scheduler.shutdown()

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    lifespan=lifespan,
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
def health_check():
    return {"status": "ok", "message": f"Welcome to {settings.app_name}!"}

app.include_router(feedback.router, prefix="/api/v1")
app.include_router(resume.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")

# Run the app (optional, for development)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)