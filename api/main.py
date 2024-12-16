import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from api.src.routes.imageGenerator import router as image_generator_router
from api.src.routes.webScrapper import router as web_scrapper_router

from fastapi.middleware.cors import CORSMiddleware

# CORS Configuration
origins = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]
app = FastAPI()



# API Router setup
api_router = APIRouter()

# Include your routers
api_router.include_router(image_generator_router, prefix="/image-generator")
api_router.include_router(web_scrapper_router, prefix="/web-scrapper")


# Add the router and middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)



# Root endpoint
@app.get("/")
async def root():
    return {"message": "Chatbot api working ..."}

