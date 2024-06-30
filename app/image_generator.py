from typing import List

from app.aihorde_image_generator import AiHordeImageGenerator
from app.article_repository import ImageGenerated, ImageToCreate
from app.settings import SD_MODEL

image_generator = AiHordeImageGenerator()


class CreatedImage:
    def __init__(self, data: bytes, model: str):
        self.data = data
        self.model = model


async def generate_images(images: List[ImageToCreate]) -> List[ImageGenerated]:
    images_generated = []
    for img_gen in images:
        created = await image_generator.create_image(img_gen.prompt)
        images_generated.append(ImageGenerated(img_gen.img_id, img_gen, created, SD_MODEL))
    return images_generated
