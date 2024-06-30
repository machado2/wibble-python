from uuid import uuid4

from fastapi import APIRouter, Request, BackgroundTasks
from starlette.responses import HTMLResponse, RedirectResponse

from app.article_generator import create_article
from app.template import render_template
from app.wait import background_ids

router = APIRouter()


@router.get('/', response_class=HTMLResponse)
async def get_create(request: Request):
    return render_template("create.html", request)


async def create_article_and_remove_task(identifier: str, prompt: str):
    try:
        await create_article(identifier, prompt)
    finally:
        background_ids.pop(identifier, None)


@router.post('/')
async def post_create(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    prompt = form.get('prompt')
    identifier = str(uuid4())
    background_ids[identifier] = True
    background_tasks.add_task(create_article_and_remove_task, identifier, prompt)
    return RedirectResponse(url=f"/wait/{identifier}", status_code=303)
