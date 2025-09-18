import os
from PIL import Image
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
                guidance_scale: float = 5, 
                inference_steps: int = 25,
                device: str = "cuda"):
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.alpha = alpha
        self.adapter_scale = adapter_scale
        self.guidance_scale = guidance_scale
        self.inference_steps = inference_steps
        self.uploaded_images = [None, None]
        self.result_image_path = None
        self.device = device

        # Load the image encoder separately.
        self.image_encoder = CLIPVisionModelWithProjection.from_pretrained(
            "h94/IP-Adapter",
            subfolder="models/image_encoder",
            torch_dtype=torch.float16,
        ).to(self.device)

        # Load the base diffusion model and pass the image encoder.
        self.pipeline = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16,
            image_encoder=self.image_encoder,
        ).to(self.device)

        # Load the IP-Adapter weights.
        self.pipeline.load_ip_adapter(
            "h94/IP-Adapter",
            subfolder="models",
            weight_name="ip-adapter-plus_sd15.bin"
        )

    def set_parameters(self, prompt: str, negative_prompt: str, alpha: float, adapter_scale: float, guidance_scale: float, inference_steps: int):
        """Save model parameters"""
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.alpha = alpha
        self.adapter_scale = adapter_scale
        self.guidance_scale = guidance_scale
        self.inference_steps = inference_steps
    
    def upload_image(self, file, slot: int, upload_dir: str="static/uploads") -> str:
        """
        Upload and save image into slot, return uploaded image path
        
        Parameter:
        ---
        - file: image file (.png, .jpg, .webp, etc.)
        - slot: the slot of the image file (0 or 1)
        - upload_dir: upload directory, default: "static/uploads"
        """
        if not file:
            raise ValueError("No image provided")
        if slot not in (0, 1):
            raise ValueError("Slot must be 0 or 1")
    
        os.makedirs(upload_dir, exist_ok=True)

        img = Image.open(file.stream).convert("RGB")
        uploaded_path = os.path.join(upload_dir, file.filename)
        img.save(uploaded_path)
        self.uploaded_images[slot] = uploaded_path

        return uploaded_path

    def generate_result(self, output_dir: str="static/results") -> str:
        """Generate result image and return result image path"""      
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "result.png")

        filled = [img for img in self.uploaded_images if img is not None]

        if len(filled) == 2:
            img1 = load_image(filled[0])
            img2 = load_image(filled[1])

            # Prepare embeddings using IP-Adapter
            embA = self.pipeline.prepare_ip_adapter_image_embeds(
                ip_adapter_image=img1,
                ip_adapter_image_embeds=None,
                device=self.device,
                num_images_per_prompt=1,
                do_classifier_free_guidance=True
            )
            embB = self.pipeline.prepare_ip_adapter_image_embeds(
                ip_adapter_image=img2,
                ip_adapter_image_embeds=None,
                device=self.device,
                num_images_per_prompt=1,
                do_classifier_free_guidance=True
            )
            self.pipeline.set_ip_adapter_scale(self.adapter_scale)

            # Weighted fusion
            image_embed = [self.alpha * a + (1 - self.alpha) * b for a, b in zip(embA, embB)]
        
        elif len(filled) == 1:
            img1 = load_image(filled[0])
            image_embed = self.pipeline.prepare_ip_adapter_image_embeds(
                ip_adapter_image=img1,
                ip_adapter_image_embeds=None,
                device=self.device,
                num_images_per_prompt=1,
                do_classifier_free_guidance=True
            )
            self.pipeline.set_ip_adapter_scale(self.adapter_scale)
        else: 
            raise ValueError("No image provided. Please upload images.")

        # Generate image
        out = self.pipeline(
            prompt=self.prompt,
            negative_prompt=self.negative_prompt,
            ip_adapter_image_embeds=image_embed,
            num_inference_steps=self.inference_steps,
            guidance_scale=self.guidance_scale,
        ).images[0]

        out.save(output_path)
        self.result_image_path = output_path

        return output_path

    def get_result(self) -> str:
        """Return path of generated result image"""
        if not self.result_image_path:
            raise FileNotFoundError("Result image not found.")
        return self.result_image_path
