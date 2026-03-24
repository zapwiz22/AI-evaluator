from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, evaluate

app = FastAPI(title="AI Evaluator API")

# Allow requests from your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our upload router
app.include_router(upload.router)
app.include_router(evaluate.router)

@app.get("/")
def root():
    return {"message": "AI Evaluator Backend is running"}