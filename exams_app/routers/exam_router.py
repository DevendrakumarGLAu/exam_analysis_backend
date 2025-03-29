from fastapi import APIRouter
from exams_app.api_v1.exam_api_v1 import exam_router

api_router = APIRouter()

api_router.include_router(exam_router, prefix="/api/v1", tags=["Exams"])
