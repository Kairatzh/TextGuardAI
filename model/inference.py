from configs.config import load_configs
import torch
import pickle
from model.train import TextPreprocessor

configs = load_configs()

model = configs["model"]["model_path"]
vectorizer = configs["model"]["vectorizer_path"]

model = torch.load(model)
vectorizer = pickle.load(open(vectorizer, "rb"))

preprocessor = TextPreprocessor()

def predict_inference(text: str):
    text = preprocessor.preprocess(text)
    text = vectorizer.transform([text])
    text = text.toarray()
    text = torch.tensor(text, dtype=torch.float32)
    text = text.unsqueeze(0)
    output = model(text)
    output = output.argmax(dim=1)
    return output.item()