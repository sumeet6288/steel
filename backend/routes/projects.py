from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.project import Project, ProjectCreate, ProjectUpdate
from utils.dependencies import get_current_user
from typing import List
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

router = APIRouter(prefix="/projects", tags=["projects"])

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

@router.post("/", response_model=Project)
async def create_project(project_create: ProjectCreate, user_id: str = Depends(get_current_user)):
    project = Project(**project_create.model_dump(), user_id=user_id)
    doc = project.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.projects.insert_one(doc)
    return project

@router.get("/", response_model=List[Project])
async def get_projects(user_id: str = Depends(get_current_user)):
    projects = await db.projects.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    
    for project in projects:
        if isinstance(project['created_at'], str):
            project['created_at'] = datetime.fromisoformat(project['created_at'])
        if isinstance(project['updated_at'], str):
            project['updated_at'] = datetime.fromisoformat(project['updated_at'])
    
    return [Project(**p) for p in projects]

@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str, user_id: str = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id, "user_id": user_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    if isinstance(project['created_at'], str):
        project['created_at'] = datetime.fromisoformat(project['created_at'])
    if isinstance(project['updated_at'], str):
        project['updated_at'] = datetime.fromisoformat(project['updated_at'])
    
    return Project(**project)

@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, project_update: ProjectUpdate, user_id: str = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id, "user_id": user_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    update_data = project_update.model_dump(exclude_unset=True)
    if update_data:
        update_data['updated_at'] = datetime.now().isoformat()
        await db.projects.update_one({"id": project_id}, {"$set": update_data})
    
    updated_project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if isinstance(updated_project['created_at'], str):
        updated_project['created_at'] = datetime.fromisoformat(updated_project['created_at'])
    if isinstance(updated_project['updated_at'], str):
        updated_project['updated_at'] = datetime.fromisoformat(updated_project['updated_at'])
    
    return Project(**updated_project)

@router.delete("/{project_id}")
async def delete_project(project_id: str, user_id: str = Depends(get_current_user)):
    result = await db.projects.delete_one({"id": project_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    await db.connections.delete_many({"project_id": project_id})
    
    return {"message": "Project deleted successfully"}