import sys
import asyncio

# On Windows, set the Proactor event loop early to fix subprocess errors
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import os
import django

# Setup Django before importing your models or routers that use Django ORM
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exam_analysis.settings")
django.setup()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from exams_app.api_v1.exam_api_v1 import api_router
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}

@app.get("/test-external-request")
def test_external_request():
    try:
        response = requests.get("https://httpbin.org/ip")
        return {"status_code": response.status_code, "response": response.json()}
    except Exception as e:
        return {"error": str(e)}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
