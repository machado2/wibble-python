import asyncio
from typing import List

from app.aihorde_image_generator import AiHordeImageGenerator
from app.article_repository import ImageGenerated, ImageToCreate
from settings import SD_MODEL

image_generator = AiHordeImageGenerator()


class CreatedImage:
    def __init__(self, data: bytes, model: str):
        self.data = data
        self.model = model


async def generate_images(images: List[ImageToCreate]) -> List[ImageGenerated]:
    # Create tasks for generating images
    tasks = [image_generator.create_image(img_gen.prompt) for img_gen in images]
    # Run tasks in parallel and wait for all to complete
    created_images = await asyncio.gather(*tasks)
    # Create ImageGenerated objects
    images_generated = [ImageGenerated(img_gen.img_id, img_gen, created, SD_MODEL) for img_gen, created in
                        zip(images, created_images)]
    return images_generated
