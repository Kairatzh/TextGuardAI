from fastapi import FastAPI
from app.schemas import TextInput, TextOutput
import uvicorn
from model.inference import predict_inference
from configs.config import load_configs

configs = load_configs()

app = FastAPI()

@app.post("/predict", responce_model=TextOutput)
async def predict(input: TextInput):
    output = await predict_inference(input.text)
    return TextOutput(toxicity=output.item())

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host=configs["app"]["host"], port=configs["app"]["port"])
