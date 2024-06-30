import markdown_it
from fastapi import APIRouter, HTTPException, Request
from starlette.responses import HTMLResponse

from app.models import Content
from app.template import render_template

router = APIRouter()

markdown = markdown_it.MarkdownIt()


@router.get("/{slug}", response_class=HTMLResponse)
async def get_content(request: Request, slug: str):
    content = await Content.filter(slug=slug).first()
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
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
