import requests
from requests.exceptions import RequestException
import base64

from model.predict_response import PredictResponse

api_url = "https://our-model-api.nick_hopefully_set_this_up.com/predict"


def send_photo_to_api(photo_base64: str) -> PredictResponse:
    if is_base64(photo_base64):
        try:
            response = requests.post(api_url, json={"photo_base64": photo_base64})
            print(f"Response: {response}")
            response.raise_for_status()
            response = PredictResponse.model_validate(response.json())
            print(f"Response: {response}")
            return response
        except RequestException as e:
            print(f"Error: {e}")
            raise e
    else:
        raise ValueError("The photo is not a valid base64 string")


def is_base64(s: str) -> bool:
    try:
        return base64.b64encode(base64.b64decode(s)) == s
    except Exception:
        return False
