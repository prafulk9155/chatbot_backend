from fastapi import FastAPI

# Import the API router from the api folder
from router.test import api

app = FastAPI()

# Mount the API router to the main application
app.include_router(api, prefix="/api")  # Set the base URL for API routes



# To run the application, use:
# uvicorn main:app --reload