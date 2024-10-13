from fastapi import APIRouter 
from fastapi import Request, Form
import warnings
from api.scraper import *

warnings.filterwarnings("ignore")
router = APIRouter()

@router.get("/")
def read_root():
    return {"Status": "Scraper api working"}


@router.post("/scrapeWeb", tags=['web'])
async def scrape_web(request : Request):
    '''Router for Scraping Web url and store the emmbedding to pinecodesb'''
    try:
        request_body = await request.body()
        input_data = json.loads(request_body.decode('utf-8'))['data'] 
        data = web_to_vectordb(input_data) 
        return data 
    except Exception as e:
        return {"error": True, "message": f"Some error occurred in: {str(e)}"}