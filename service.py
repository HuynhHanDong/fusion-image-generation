from model import ImageModel

model = ImageModel()

def handle_upload(files, slot: int):
    if not files:
        return ValueError("No image uploaded.")
    if slot not in (0, 1):
        raise ValueError("Invalid slot")
    return model.upload_images(files, slot, upload_dir="static/uploads")

def clear_slot(slot: int):
    if slot not in (0, 1):
        raise ValueError("Invalid slot")
    model.uploaded_images[slot] = None

def get_parameter():
    return {
        "prompt": model.prompt,
        "negative_prompt": model.negative_prompt,
        "alpha": model.alpha,
        "adapter_scale": model.adapter_scale,
        "guidance_scale": model.guidance_scale,
        "inference_steps": model.inference_steps
    }

def generate_and_show(dto):
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

def get_result():
    return model.get_result()