from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse, RedirectResponse
from uuid import uuid4

from app.template import render_template

router = APIRouter()


@router.get('/', response_class=HTMLResponse)
async def get_create(request: Request):
    return render_template("create.html", request)

@router.post('/')
async def post_create(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    prompt = form.get('prompt')
    identifier = str(uuid4())
    background_tasks.add_task(create_article, identifier, prompt)
    return RedirectResponse(url=f"/wait/{identifier}", status_code=303)