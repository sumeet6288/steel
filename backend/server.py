from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from routes import auth, projects, connections, redlines, audit, ai

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="SteelConnect AI API", version="1.0.0")

api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def root():
    return {
        "message": "SteelConnect AI - AI-Assisted Steel Connection Detailing",
        "version": "1.0.0",
        "disclaimer": "Advisory tool for US steel fabricators. Engineering review required."
    }

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SteelConnect AI"}

api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(connections.router)
api_router.include_router(redlines.router)
api_router.include_router(audit.router)
api_router.include_router(ai.router)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()