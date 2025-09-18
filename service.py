from model import ImageModel

model = ImageModel()

def upload_image(files, slot: int) -> str:
    uploaded_path = model.upload_image(files, slot, upload_dir="static/uploads")
    return uploaded_path

def clear_slot(slot: int) -> None:
    if slot not in (0, 1):
        raise ValueError("Invalid slot")
    model.uploaded_images[slot] = None

def get_parameter() -> dict[str, any]:
    return {
        "prompt": model.prompt,
        "negative_prompt": model.negative_prompt,
        "alpha": model.alpha,
        "adapter_scale": model.adapter_scale,
        "guidance_scale": model.guidance_scale,
        "inference_steps": model.inference_steps
    }

def generate_and_show(dto) -> str:
    # Save params
    model.set_parameters(
        dto.prompt,
        dto.negative_prompt,
        dto.alpha,
        dto.adapter_scale,
        dto.guidance_scale,
        dto.inference_steps
    )

    # Run generation
    result_path = model.generate_result(output_dir="static/results")
    return result_path

def get_result() -> str:
    result_path = model.get_result()
    return result_path