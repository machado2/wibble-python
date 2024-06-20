from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import HTMLResponse

from app.config import templates
from app.db import get_session
from app.models import Content
import markdown_it

router = APIRouter()

markdown = markdown_it.MarkdownIt()


@router.get("/{slug}", response_class=HTMLResponse)
async def get_content(request: Request, slug: str, db: AsyncSession = Depends(get_session)):
    # noinspection PyTypeChecker
    query = select(Content).where(Content.slug == slug)
    result = await db.execute(query)
    content = result.scalar_one_or_none()
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    html = markdown.render(content.markdown or "")
    return templates.TemplateResponse("content.html", {
        "request": request,
        "id": content.id,
        "slug": content.slug,
        "created_at": content.created_at.strftime("%Y-%m-%d"),
        "description": content.description,
        "image_id": content.image_id or "",
        "title": content.title,
        "body": html,
    })
