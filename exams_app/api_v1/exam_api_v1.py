# exams_app/api_v1/exam_api_v1.py
from fastapi import APIRouter, HTTPException
# from controllers.rrb_je_controller import RRBJEController  # Import the controller
from exams_app.controllers.rrb_je_controller import RRBJEController
from exams_app.controllers.rrb_constable_controller import RRBConstableController
from exams_app.controllers.ssc_exam_controller import SSCExamController
from exams_app.schema import ScrapeRequest 

api_router = APIRouter()

@api_router.get("/exams")
def get_exams():
    return {"exams": ["exam1", "exam2", "exam3"]}

@api_router.post("/scrape-exam-data")
def scrape_exam_data(request:ScrapeRequest):
    try:
        data = RRBJEController.fetch_exam_data(
            request.url, request.category, request.Horizontalcategory,
            request.Exam_Language, request.RRB_zone, request.RRB_branch
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred in railway je: {str(e)}")

@api_router.post("/rrb-constable-exam-data")
def scrape_exam_data(request:ScrapeRequest):
    try:
        data = RRBConstableController.fetch_exam_data(
            request.url, request.category, request.Horizontalcategory,
            request.Exam_Language, request.RRB_zone, request.password, request.exam_type
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred in railway constable: {str(e)}")

    
@api_router.post("/ssc-exam-data")
def scrape_exam_data(request:ScrapeRequest):
    try:
        data = SSCExamController.fetch_ssc_exam_data(
            request.url, request.category, request.Horizontalcategory,
            request.Exam_Language, request.exam_type, request.password
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred in ssc: {str(e)}")

