from fastapi import  HTTPException,APIRouter


from pydantic import BaseModel
import requests
from api.src.controllers.imageGenerator import *

router = APIRouter()


@router.get("/")
async def main():
    try:
        val = mainApi() 
        return val
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
