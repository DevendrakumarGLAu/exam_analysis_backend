from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from exams_app.api_v1.exam_api_v1 import api_router

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
# ✅ Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this for security)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# ✅ Include API Router
app.include_router(api_router, prefix="/api/v1")

