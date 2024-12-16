from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
from difflib import SequenceMatcher

router = APIRouter()

# Dataset API URLs
DATASET_URLS = {
    "dataset_one": "https://datasets-server.huggingface.co/rows?dataset=data-is-better-together%2Fopen-image-preferences-v1-binarized&config=default&split=train&offset=0&length=100",
    "dataset_two": "https://datasets-server.huggingface.co/rows?dataset=mengcy%2FLAION-SG&config=default&split=train&offset=0&length=100"
}

# Helper function for similarity calculation
def calculate_similarity(prompt1: str, prompt2: str) -> float:
    return SequenceMatcher(None, prompt1, prompt2).ratio()

# Request model
class PromptRequest(BaseModel):
    prompt: str

@router.post("/match-image/")
async def match_image(request: PromptRequest):
    user_prompt = request.prompt

    results = []

    # Fetch and process each dataset
    for dataset_name, dataset_url in DATASET_URLS.items():
        response = requests.get(dataset_url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Failed to fetch data from {dataset_name}.")

        data = response.json()
        matched_image = None
        exact_match = None

        # Check similarity within the dataset
        for row in data["rows"]:
            if dataset_name == "dataset_one":
                dataset_prompt = row["row"]["prompt"]
                chosen_image = row["row"]["chosen"]["src"]
                rejected_image = row["row"]["rejected"]["src"]
            elif dataset_name == "dataset_two":
                dataset_prompt = row["row"]["caption_ori"]
                chosen_image = row["row"]["url"]
                rejected_image = None

            similarity = calculate_similarity(user_prompt, dataset_prompt)

            # Check for exact match (100%)
            if similarity == 1.0:
                exact_match = {
                    "dataset": dataset_name,
                    "prompt": dataset_prompt,
                    "similarity": similarity,
                    "chosen_image": chosen_image,
                    "rejected_image": rejected_image,
                }
                break  # No need to check further

            # Check for matches with similarity >= 30%
            if similarity >= 0.3 and not exact_match:
                matched_image = {
                    "dataset": dataset_name,
                    "prompt": dataset_prompt,
                    "similarity": similarity,
                    "chosen_image": chosen_image,
                    "rejected_image": rejected_image,
                }

        # Prioritize exact match, fallback to partial match
        if exact_match:
            results.append(exact_match)
        elif matched_image:
            results.append(matched_image)

    if not results:
        raise HTTPException(status_code=404, detail="No matching image found across datasets.")

    return results
