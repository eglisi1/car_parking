from pydantic import BaseModel

class PredictRequest(BaseModel):
    photo_base64: str
