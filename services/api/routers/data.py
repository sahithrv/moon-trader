from fastapi import APIRouter

from models.config import Symbol


router = APIRouter(prefix="/data", tags=["data"])


#@router.post("/backfill")


