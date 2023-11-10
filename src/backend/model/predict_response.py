from pydantic import BaseModel

class PredictResponse(BaseModel):
    photo_base64: str
    instructions: str
