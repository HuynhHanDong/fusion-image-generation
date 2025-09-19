# Fusion Image Generation
This project is a demo web application for **image fusion using IP-Adapter**.

Users can upload up to two reference images, set text prompts and generation parameters, and produce a fused output image using Stable Diffusion with IP-Adapter embeddings.  

The project is designed for demonstration purposes — it does not handle user sessions, file collisions, or production-level security.

## ⚙️ Features
- Upload up to **two reference images** (slot-based, optional: 0–2 images)
- Text prompt + negative prompt input
- Adjustable parameters:
  - Alpha (blend ratio)
  - Adapter scale
  - Inference steps
  - Guidance scale
- Clear buttons for each image slot
- Placeholder UI for uploads and result box
- Download generated result

## 📝 Notes

- By default, generated images are saved as `static/results/result.png`.
- To prevent caching issues, the frontend appends a **cache-busting query string** to image URLs.
- For demo simplicity:
  - No session or user separation
  - No duplicate filename handling
- To support multiple generations, you can modify the backend to save results with **unique filenames** (e.g. UUID).

## 🚀 Technology stack
**Backend:**
- Python
- Flask
- Pydantic
- Torch
- Diffusers (Stable Diffusion pipeline with IP-Adapter)
- Transformers
- Pillow

**Frontend:**
  - HTML
  - CSS
  - JavaScript

## 📂 Project Structure
```
fusion-image-generation/
│
├── app.py            # Flask entrypoint, API routes (/upload, /generate, /clear_slot, etc.)
├── service.py        # Service layer connecting Flask routes to model logic
├── model.py          # ImageModel class, handles uploads, parameters, and generation
│
├── static/
│ ├── styles.css      # Styles for the frontend (cards, upload boxes, buttons, etc.)
│ ├── script.js       # Frontend logic: upload, clear, generate, download
│ └── uploads/        # Uploaded images (slot 0 / slot 1)
│ └── results/        # Generated result images
│
├── templates/
│ └── index.html      # Main frontend page
│
├── requirements.txt 
├── .gitignore    
└── README.md         # Project documentation
```

## ▶️ Running the Project

1. Clone the repository

```bash
git clone https://github.com/HuynhHanDong/fusion-image-generation.git
cd https://github.com/HuynhHanDong/fusion-image-generation.git
```
2. Create and activate a virtual environment

&emsp;&emsp;```python -m venv venv```

&emsp;&emsp;Windows:  
&emsp;&emsp;&emsp; ```.venv\Scripts\Activate.ps1``` (powershell)  
&emsp;&emsp;&emsp; ```.venv\Scripts\activate``` (command prompt)  

&emsp;&emsp;macOS/Linux:  ```source .venv/bin/activate```  

3. Install dependencies:

&emsp;&emsp; ```pip install -r requirements.txt```  

4. Run the Flask app:

&emsp;&emsp; ```python app.py```

5. Open your browser at:

&emsp;&emsp; ```http://127.0.0.1:5000/```