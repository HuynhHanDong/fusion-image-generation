import os
import torch
from diffusers import StableDiffusionPipeline
from transformers import CLIPVisionModelWithProjection
from diffusers.utils import load_image

class ImageModel:
    def __init__(self, 
                prompt: str = "A hybrid composition merging both references", 
                negative_prompt: str = "blur, low quality, bad anatomy", 
                alpha: float = 0.5, 
                adapter_scale: float = 0.8, 
                guidance_scale: float = 2, 
                inference_steps: int = 20):
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.alpha = alpha
        self.adapter_scale = adapter_scale
        self.guidance_scale = guidance_scale
        self.inference_steps = inference_steps
        self.uploaded_images = []
        self.result_image_path = None

    def set_parameters(self, prompt: str, negative_prompt: str, alpha: float, adapter_scale: float, guidance_scale: float, inference_steps: int):
        """Save model parameters (prompt, alpha, scale, etc.)"""
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.alpha = alpha
        self.adapter_scale = adapter_scale
        self.guidance_scale = guidance_scale
        self.inference_steps = inference_steps
    
    def set_up_model(self):
        device = "cuda"

        # Load the image encoder separately.
        image_encoder = CLIPVisionModelWithProjection.from_pretrained(
            "h94/IP-Adapter",
            subfolder="models/image_encoder",
            torch_dtype=torch.float16,
        ).to(device)

        # Load the base diffusion model and pass the image encoder.
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16,
            image_encoder=image_encoder,
        ).to(device)

        # Load the IP-Adapter weights.
        pipe.load_ip_adapter(
            "h94/IP-Adapter",
            subfolder="models",
            weight_name="ip-adapter-plus_sd15.bin"
        )
        return pipe
    
    def upload_images(self, files, upload_dir="uploads"):
        """
        Save multiple uploaded images using diffusers.utils.load_image.
        Returns list of saved paths.
        """
        os.makedirs(upload_dir, exist_ok=True)
        self.uploaded_images = []  # reset

        saved_paths = []
        for file in files:
            # Flask `FileStorage` -> read bytes
            image = load_image(file)
            path = os.path.join(upload_dir, file.filename)
            image.save(path)  # save with PIL's save()
            self.uploaded_images.append(path)
            saved_paths.append(path)

        return saved_paths

    def generate_result(self, pipeline, device, output_dir="static/results"):
        """
        Dummy generation: copy uploaded image & pretend it's processed.
        Replace with your actual ML pipeline.
        """
        if not self.uploaded_image_path:
            raise ValueError("No uploaded image to process.")
        
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "result.png")

        imgA = self.uploaded_images[0]
        imgB = self.uploaded_images[1]

        # Prepare embeddings using IP-Adapter
        embA = pipeline.prepare_ip_adapter_image_embeds(
            ip_adapter_image=imgA,
            ip_adapter_image_embeds=None,
            device=pipeline,
            num_images_per_prompt=1,
            do_classifier_free_guidance=True
        )
        embB = pipeline.prepare_ip_adapter_image_embeds(
            ip_adapter_image=imgB,
            ip_adapter_image_embeds=None,
            device=device,
            num_images_per_prompt=1,
            do_classifier_free_guidance=True
        )

        # Weighted fusion
        combined_emb = [self.alpha * a + (1 - self.alpha) * b for a, b in zip(embA, embB)] 

        pipeline.set_ip_adapter_scale(self.adapter_scale)

        # Generate image
        out = pipeline(
            prompt=self.prompt,
            negative_prompt=self.negative_prompt,
            ip_adapter_image_embeds=combined_emb,
            num_inference_steps=self.inference_steps,
            guidance_scale=self.guidance_scale,
        ).images[0]

        out.save(output_path)
        self.result_image_path = output_path

        return output_path

    def get_result(self):
        """Return path of generated result"""
        if not self.result_image_path:
            raise ValueError("No result generated yet.")
        return self.result_image_path
