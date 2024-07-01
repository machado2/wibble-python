from uuid import uuid4

import markdown_it
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from starlette.responses import HTMLResponse, RedirectResponse

from app.create import create_article_and_remove_task
from app.models import Content
from app.template import render_template
from app.wait import background_ids

router = APIRouter()

markdown = markdown_it.MarkdownIt()


@router.get("/{slug}", response_class=HTMLResponse)
async def get_content(request: Request, background_tasks: BackgroundTasks, slug: str):
    content = await Content.filter(slug=slug).first()
    if content is None:
        identifier = str(uuid4())
        background_ids[identifier] = True
        background_tasks.add_task(create_article_and_remove_task, identifier, slug)
        return RedirectResponse(url=f"/wait/{identifier}", status_code=303)
    html = markdown.render(content.markdown or "")
    return render_template(
        "content.html", request,
        id=content.id,
        slug=content.slug,
        created_at=content.created_at.strftime("%Y-%m-%d"),
        description=content.description,
        image_id=content.image_id or "",
        title=content.title,
        body=html
    )
