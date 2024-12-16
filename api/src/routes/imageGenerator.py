from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
from difflib import SequenceMatcher

router = APIRouter()

# Hugging Face Dataset API URL
DATASET_URL = (
    "https://datasets-server.huggingface.co/rows"
    "?dataset=data-is-better-together%2Fopen-image-preferences-v1-binarized"
    "&config=default&split=train&offset=0&length=100"
)

# Helper function for similarity calculation
def calculate_similarity(prompt1: str, prompt2: str) -> float:
    return SequenceMatcher(None, prompt1, prompt2).ratio()

# Request model
class PromptRequest(BaseModel):
    prompt: str

# @router.post("/match-image/")
# async def match_image(request: PromptRequest):
#     user_prompt = request.prompt

#     # Fetch dataset
#     response = requests.get(DATASET_URL)
#     if response.status_code != 200:
#         raise HTTPException(status_code=500, detail="Failed to fetch dataset.")
    
#     data = response.json()
#     matched_image = None

#     # Check similarity
#     for row in data["rows"]:
#         dataset_prompt = row["row"]["prompt"]
#         similarity = calculate_similarity(user_prompt, dataset_prompt)
        
#         if similarity >= 0.3:  # If similarity is 30% or higher
#             matched_image = {
#                 "prompt": dataset_prompt,
#                 "similarity": similarity,
#                 "chosen_image": row["row"]["chosen"]["src"],
#                 "rejected_image": row["row"]["rejected"]["src"],
#             }
#             break
    
#     if not matched_image:
#         raise HTTPException(status_code=404, detail="No matching image found.")
    
#     return matched_image

@router.post("/match-image/")
async def match_image(request: PromptRequest):
    user_prompt = request.prompt

    # Fetch dataset
    response = requests.get(DATASET_URL)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch dataset.")
    
    data = response.json()
    matched_image = None
    exact_match = None

    # Check similarity
    for row in data["rows"]:
        dataset_prompt = row["row"]["prompt"]
        similarity = calculate_similarity(user_prompt, dataset_prompt)
        
        # Check for exact match (100%)
        if similarity == 1.0:
            exact_match = {
                "prompt": dataset_prompt,
                "similarity": similarity,
                "chosen_image": row["row"]["chosen"]["src"],
                "rejected_image": row["row"]["rejected"]["src"],
            }
            break  # No need to check further
        
        # Check for matches with similarity >= 30%
        if similarity >= 0.1 and not exact_match:
            matched_image = {
                "prompt": dataset_prompt,
                "similarity": similarity,
                "chosen_image": row["row"]["chosen"]["src"],
                "rejected_image": row["row"]["rejected"]["src"],
            }

    # Prioritize exact match, fallback to partial match
    if exact_match:
        return exact_match
    elif matched_image:
        return matched_image
    
    # No match found
    raise HTTPException(status_code=404, detail="No matching image found.")

