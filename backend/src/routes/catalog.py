from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.controllers.dependencies import current_user,writers
from src.schemas.study import StudyInput
from src.schemas.cell import CellPatch,CategoryPatch
from src.services import catalog
router=APIRouter()
@router.get('/studies')
def studies(db:Session=Depends(get_db),user=Depends(current_user)):return catalog.studies(db)
@router.post('/studies',status_code=201)
def create(data:StudyInput,db:Session=Depends(get_db),user=Depends(writers)):return catalog.create_study(db,data,user)
@router.get('/categories')
def categories(db:Session=Depends(get_db),user=Depends(current_user)):return catalog.categories(db)
@router.patch('/categories/{id}')
def category(id:int,data:CategoryPatch,db:Session=Depends(get_db),user=Depends(writers)):return catalog.patch_category(db,id,data,user)
@router.get('/cells')
def cells(db:Session=Depends(get_db),user=Depends(current_user)):return catalog.cells(db)
@router.patch('/cells/{id}')
def cell(id:int,data:CellPatch,db:Session=Depends(get_db),user=Depends(writers)):return catalog.patch_cell(db,id,data,user)
