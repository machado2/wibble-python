import uuid

from slugify import slugify
from tortoise.transactions import in_transaction

from app.models import Content, ImageData, ContentImage


async def get_slug_for(title: str) -> str:
    slug = slugify(title)
    existing_content = await Content.filter(slug__contains=slug).first()
    return slug if existing_content is None else str(uuid.uuid4())


async def save_image(article_id: str, prompt: str, alt_text: str, model: str, image_id: str, img: bytes):
    async with in_transaction() as db:
        try:
            content_image = ContentImage(id=image_id, content_id=article_id, prompt=prompt, alt_text=alt_text,
                                         model=model)
            await content_image.save(using_db=db)
            image_data = ImageData(id=image_id, jpeg_data=img)
            await image_data.save(using_db=db)
        except Exception as e:
            await db.rollback()
            raise e


class ImageToCreate:
    def __init__(self, img_id: str, caption: str, prompt: str):
        self.img_id = img_id
        self.caption = caption
        self.prompt = prompt


class ImageGenerated:
    def __init__(self, img_id: str, img: ImageToCreate, data: bytes, model: str):
        self.img_id = img_id
        self.img = img
        self.data = data
        self.model = model


class Article:
    def __init__(self, article_id: str, title: str, markdown: str, instructions: str, start_time: str, model: str,
                 description: str, images: list[ImageGenerated]):
        self.article_id = article_id
        self.title = title
        self.markdown = markdown
        self.instructions = instructions
        self.start_time = start_time
        self.model = model
        self.description = description
        self.images = images


async def save_article(article: Article):
    slug = await get_slug_for(article.title)
    first_image_id = article.images[0].img_id if article.images else None

    async with in_transaction() as db:
        try:
            content = Content(
                id=article.article_id,
                slug=slug,
                content=article.markdown,
                title=article.title,
                user_input=article.instructions,
                description=article.description,
                image_id=first_image_id
            )
            await content.save(using_db=db)

            for img in article.images:
                await save_image(article.article_id, img.img.prompt, img.img.caption,
                                 img.model, img.img_id, img.data)

            await content.save(using_db=db)
        except Exception as e:
            await db.rollback()
            raise e
