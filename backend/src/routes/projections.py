from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.controllers.dependencies import current_user, writers
from src.schemas.projection import ProjectionInput
from src.services import projection
router = APIRouter()


@router.post('/projections', status_code=201)
def create(data: ProjectionInput, db: Session = Depends(get_db), user=Depends(writers)):
    return projection.project_supplementary(db, data, user)
