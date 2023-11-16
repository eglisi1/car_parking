import unittest
import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Add the parent directory of 'src' to the Python path.
# So we can run the test from the src/backend directory
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Now main and others can be imported
from main import app
from model.predict_request import PredictRequest


class TestMain(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_predict_nok(self):
        request = PredictRequest(photo_base64="not a base64 string")
        response = self.client.put("/predict", json=request.model_dump())
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
