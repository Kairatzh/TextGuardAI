from fastapi import FastAPI
from app.schemas import TextInput, TextOutput
import uvicorn



app = FastAPI()

@app.post("/predict", responce_model=TextOutput)
async def predict(input: TextInput):
    
