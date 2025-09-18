from pydantic import BaseModel, Field

class requestDTO(BaseModel):
    prompt: str = Field(..., min_length=0)
    negative_prompt: str = Field(..., min_length=0)
    alpha: float = Field(..., gt=0, lt=1)
    adapter_scale: float = Field(..., gt=0, lt=1)
    guidance_scale: float = Field(..., gt=0, lt=15)
    inference_steps: int = Field(..., gt=0, lt=100)
