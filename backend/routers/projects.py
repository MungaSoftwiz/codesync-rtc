from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class Project(BaseModel):
    name: str
    description: str
    owner: str


projects_db = {}


@router.post("/create")
def create_project(project: Project):
    if project.name in projects_db:
        raise HTTPException(status_code=400, detail="Project name already exists")
    projects_db[project.name] = project
    return {"message": "Project created successfully"}


@router.get("/{project_name}")
def get_project(project_name: str):
    if project_name not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects_db[project_name]
