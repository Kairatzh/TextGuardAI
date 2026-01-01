from pydantic import BaseModel, Field
from typing import List

class TextInput(BaseModel):
    text: str = Field(..., description="The text to classify") #Text to classify

class TextOutput(BaseModel):
    toxicity: float = Field(..., description="The toxicity") #0 - Toxic, 1 - Non-toxic