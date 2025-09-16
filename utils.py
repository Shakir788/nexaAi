import io, base64
from PIL import Image

def image_to_base64_bytes(image:Image.Image):
    b = io.BytesIO()
    image.save(b, format='PNG')
    return base64.b64encode(b.getvalue()).decode('utf-8')
