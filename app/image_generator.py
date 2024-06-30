import asyncio
from typing import List, Optional

from app.aihorde_image_generator import AiHordeImageGenerator
from app.article_repository import ImageGenerated, ImageToCreate

image_generator = AiHordeImageGenerator()


class CreatedImage:
    def __init__(self, data: bytes, model: str):
        self.data = data
        self.model = model


class ImageGeneration:
    def __init__(self, img: ImageToCreate, handle: asyncio.Future):
        self.img = img
        self.handle = handle

    async def wait(self) -> Optional[ImageGenerated]:
        try:
            data = await self.handle
            return ImageGenerated(self.img.id, self.img, data.data, data.model)
        except Exception as e:
            print(f"Failed to create image: {e}")
            return None

    @staticmethod
    def create(img_to_create: ImageToCreate) -> 'ImageGeneration':
        async def create_image_inner(prompt: str) -> CreatedImage:
            print(f"Creating image for {prompt}")
            img = await image_generator.create_image(prompt)
            if img is None:
                print(f"Failed to create image for {prompt}")
            else:
                print(f"Created image for {prompt}")
            return img

        handle = asyncio.create_task(create_image_inner(img_to_create.prompt))
        return ImageGeneration(img_to_create, handle)


async def generate_images(images: List[ImageToCreate]) -> List[ImageGenerated]:
    image_generations = [ImageGeneration.create(img) for img in images]
    images_generated = []
    for img_gen in image_generations:
        img = await img_gen.wait()
        if img is not None:
            images_generated.append(img)
    return images_generated
