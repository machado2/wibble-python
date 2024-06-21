from app.config import USE_EXAMPLES, LANGUAGE_MODELS

from app.models import Article
from app.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio

import os
import logging
from fastapi import FastAPI, HTTPException
import re
import uuid
from fastapi import HTTPException
from datetime import datetime
import pytz


async def create_article_using_placeholders(state: AppState, id: str, instructions: str, model: str,
                                            use_examples: bool):
    llm = state.llm

    if use_examples:
        examples = await get_examples(state.db)
    else:
        examples = None

    messages = format_messages(SYSTEM_WITH_PLACEHOLDERS, examples, instructions)

    try:
        article = (await llm.request_chat(messages, model)).strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    title, article = split_title(article)
    if not title or not article:
        raise HTTPException(status_code=500, detail="No title found in article")

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
        images_to_create.append({
            "id": img_id,
            "prompt": prompt,
            "caption": alt,
        })

    images = await generate_images(state, images_to_create)

    description = markdown.split("\n\n")[0] if "\n\n" in markdown else markdown

    article_data = {
        "id": id,
        "title": title,
        "markdown": markdown,
        "instructions": instructions,
        "start_time": datetime.now(pytz.utc),
        "model": model,
        "description": description,
        "images": images,
    }

    await save_article(state.db, article_data)

    return {}

async def create_article(state: AppState, id: str, instructions: str):
    logging.debug(f"Generating article for instructions: {instructions}")
    models = LANGUAGE_MODELS
    attempts = 0

    while True:
        model = models[attempts % len(models)]
        attempts += 1
        use_examples = USE_EXAMPLES or attempts > 1
        logging.debug(f"attempt {attempts} use_examples {use_examples}")

        res = await create_article_using_placeholders(state, id, instructions, model, use_examples)

        if res:
            return res

        logging.debug(f"Attempt {attempts} failed, error: {res.error if hasattr(res, 'error') else 'unknown error'}")
        if attempts >= 3:
            logging.error(
                f"Failed to generate article after 3 attempts: {res.error if hasattr(res, 'error') else 'unknown error'}")
            raise HTTPException(status_code=500, detail="Failed to generate article after 3 attempts")