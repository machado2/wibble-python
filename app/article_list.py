import datetime
from dataclasses import dataclass
from typing import List, Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy import or_, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import HTMLResponse

from app.db import get_session
from app.models import Content
from app.template import render_template

router = APIRouter()


@dataclass
class ContentListParams:
    after_id: Optional[str] = None
    page_size: Optional[int] = None
    search: Optional[str] = None
    t: Optional[str] = None
    sort: Optional[str] = None


@dataclass
class Headline:
    id: str
    slug: str
    created_at: datetime.datetime
    description: str
    title: str
    image_id: Optional[str] = None


async def get_next_page(db: AsyncSession, params: ContentListParams) -> List[Headline]:
    page_size = 20 if not params.page_size or params.page_size > 100 else params.page_size
    query = select(Content).filter(and_(Content.flagged == False, Content.generating == False))  # noqa: E712
    if params.search:
        search_term = f"%{params.search}%"
        query = query.filter(
            or_(
                Content.slug.like(search_term),
                Content.title.like(search_term),
                Content.description.like(search_term)
            )
        )

    if params.t == "week":
        delta = datetime.timedelta(weeks=1)
    elif params.t == "month":
        delta = datetime.timedelta(days=30)
    else:
        delta = None

    if delta:
        query = query.filter(Content.created_at > datetime.datetime.utcnow() - delta)

    sort_column = {
        "most_viewed": Content.view_count,
        "hot": Content.hot_score
    }.get(params.sort, Content.created_at)

    if params.after_id:
        after_content = await db.get(Content, params.after_id)
        if after_content:
            query = query.filter(
                or_(
                    and_(Content.id != after_content.id, sort_column <= getattr(after_content, sort_column.key)),
                    sort_column < getattr(after_content, sort_column.key)
                )
            )

    query = query.order_by(desc(sort_column), desc(Content.id)).limit(page_size)

    result = await db.execute(query)
    contents = result.scalars().all()

    return [Headline(
        id=c.id,
        slug=c.slug,
        created_at=c.created_at,
        description=c.description,
        image_id=c.image_id,
        title=c.title) for c in contents]


def format_headline(h: Headline) -> dict:
    return {
        "id": h.id,
        "slug": h.slug,
        "created_at": h.created_at.strftime("%Y-%m-%d"),
        "description": h.description,
        "image_id": h.image_id,
        "title": h.title
    }


@router.get("/", response_class=HTMLResponse)
async def article_list(request: Request, params: ContentListParams = Depends(),
                       db: AsyncSession = Depends(get_session)):
    items = await get_next_page(db, params)
    formatted_items = [format_headline(item) for item in items]
    after_id = formatted_items[-1]['id'] if formatted_items else None
    return render_template("index.html", request=request, items=formatted_items, after_id=after_id)
