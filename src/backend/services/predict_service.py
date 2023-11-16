import requests
from requests.exceptions import RequestException
import base64

from model.predict_response import PredictResponse

api_url = "https://our-model-api.nick_hopefully_set_this_up.com/predict"


def is_base64(s: str) -> bool:
    """Check if a string is a valid Base64 encoded string."""
    try:
        return base64.b64encode(base64.b64decode(s)).decode("utf-8") == s
    except Exception:
        return False


def validate_base64(photo_base64: str):
    """Validate if the provided string is a valid Base64 encoded string."""
    if not is_base64(photo_base64):
        raise ValueError("The photo is not a valid base64 string")


def send_photo_to_api(photo_base64: str) -> PredictResponse:
    """Send a photo to the API and return the response."""
    validate_base64(photo_base64)
    try:
        response = requests.post(api_url, json={"photo_base64": photo_base64})
        response.raise_for_status()
        return PredictResponse.model_validate(response.json())
    except RequestException as e:
        print(f"Error while sending photo to API: {e}")
        raise e
