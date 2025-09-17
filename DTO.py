from pydantic import BaseModel, Field, validator

class requestDTO(BaseModel):
    prompt: str = Field(..., min_length=0)
    negative_prompt: str = Field(..., min_length=0)
    alpha: float = Field(..., gt=0, lt=1)
    adapter_scale: float = Field(..., gt=0, lt=1)
    guidance_scale: float = Field(..., gt=0, lt=15)
    inference_steps: int = Field(..., gt=0, lt=100)

class responseDTO(BaseModel):
    prompt: str 
    negative_prompt: str 
    alpha: float 
    adapter_scale: float 
    guidance_scale: float 
    inference_steps: int 