import logging
import re
import uuid
from datetime import datetime

from fastapi import HTTPException

from app import llm
from app.article_repository import get_slug_for
from app.examples import get_examples
from app.image_generator import ImageToCreate, generate_images
from app.models import Content, ContentImage, ImageData
from settings import USE_EXAMPLES, LANGUAGE_MODELS

with open('prompts/system_with_placeholders.txt', 'r') as file:
    SYSTEM_WITH_PLACEHOLDERS = file.read()


def split_title(markdown):
    lines = markdown.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if line:
            title = line.lstrip('#').lstrip("Title").lstrip(':').strip()
            remaining = '\n'.join(lines[i + 1:])
            return title, remaining
    return None, None


async def create_article_text(article_id: str, instructions: str, model: str, use_examples: bool) -> Content:
    started_llm_at = datetime.now()
    if use_examples:
        examples = await get_examples()
    else:
        examples = None

    messages = format_messages(SYSTEM_WITH_PLACEHOLDERS, examples, instructions)
    response: str = llm.request_chat(messages, model)
    article = response.strip()

    title, article = split_title(article)
    if not title or not article:
        raise HTTPException(status_code=500, detail="No title found in article")
    description = article.split("\n\n")[0] if "\n\n" in article else article
    slug = await get_slug_for(title)
    if not slug:
        slug = str(uuid.uuid4())
    finished_llm_at = datetime.now()
    content = await Content.create(id=article_id, title=title, content=article, user_input=instructions,
                                   description=description, model=model, slug=slug, started_llm_at=started_llm_at,
                                   finished_llm_at=finished_llm_at)

    return content


async def create_article_images(content: Content):
    article = content.content
    markdown = article
    images_to_create = []
    try:
        regex = re.compile(r'<GeneratedImage prompt="([^"]+)" alt="([^"]+)" />')
    except re.error as e:
        raise HTTPException(status_code=500, detail=f"Error creating regex: {e}")

    for cap in regex.finditer(article):
        prompt = cap.group(1)
        alt = cap.group(2)
        img_id = str(uuid.uuid4())
        markdown_img = f'![{prompt}](/image/{img_id} "{alt}")'
        markdown = markdown.replace(cap.group(0), markdown_img, 1)
        images_to_create.append(ImageToCreate(img_id, alt, prompt))

    content.started_images_at = datetime.now()
    images = await generate_images(images_to_create)
    for img in images:
        await ContentImage.create(id=img.img_id, content_id=content.id, prompt=img.img.prompt, alt_text=img.img.caption,
                                  generator="aihorde", model=img.model)
        await ImageData.create(id=img.img_id, jpeg_data=img.data)
    content.finished_images_at = datetime.now()

    content.markdown = markdown
    content.image_id = images[0].img_id if images else None
    content.finished_images_at = datetime.now()
    await content.save()


async def create_article_using_placeholders(article_id: str, instructions: str, model: str,
                                            use_examples: bool):
    content = await create_article_text(article_id, instructions, model, use_examples)
    try:
        await create_article_images(content)
    except Exception as e:
        logging.error(f"Error creating images: {e}")
        await content.delete()
        raise HTTPException(status_code=500, detail="Error creating images")


async def create_article(art_id: str, instructions: str):
    logging.debug(f"Generating article for instructions: {instructions}")
    models = LANGUAGE_MODELS
    attempts = 0

    while True:
        model = models[attempts % len(models)]
        attempts += 1
        use_examples = USE_EXAMPLES or attempts > 1
        logging.debug(f"attempt {attempts} use_examples {use_examples}")

        # try:
        await create_article_using_placeholders(art_id, instructions, model, use_examples)
        return
        # except Exception as e:
        #     logging.debug(f"Attempt {attempts} failed, error: {e}")
        #     if attempts >= 1:
        #         logging.error(
        #             f"Failed to generate article after 3 attempts: {e}")
        #         raise HTTPException(status_code=500, detail="Failed to generate article after 3 attempts")


def format_messages(system_message, examples, instructions):
    messages = [{"type": "System", "content": system_message}]
    if examples is not None:
        for prompt, article in examples:
            messages.append({"type": "User", "content": prompt})
            messages.append({"type": "Assistant", "content": article})
    messages.append({"type": "User", "content": instructions})
    return messages
