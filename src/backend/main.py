from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from model.predict_response import PredictResponse
from model.predict_request import PredictRequest

from services import predict_service

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root() -> str:
    return "Be patient, this is a work in progress, but it will be awesome! Or read the docs at /docs"


@app.put("/predict")
def predict(request: PredictRequest) -> PredictResponse:
    print("Access to /predict")
    try:
        return predict_service.send_photo_to_api(request.photo_base64)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
