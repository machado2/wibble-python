import datetime
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Request
from starlette.responses import HTMLResponse
# noinspection PyPackageRequirements
from tortoise.expressions import Q

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
    created_at: datetime
    description: str
    title: str
    image_id: Optional[str] = None


async def get_next_page(params: ContentListParams) -> List[Headline]:
    page_size = 20 if not params.page_size or params.page_size > 100 else params.page_size
    query = Content.filter(flagged=False)

    if params.search:
        query = query.filter(
            Q(slug__icontains=params.search) |
            Q(title__icontains=params.search) |
            Q(description__icontains=params.search)
        )

    if params.t == "week":
        delta = timedelta(weeks=1)
    elif params.t == "month":
        delta = timedelta(days=30)
    else:
        delta = None

    if delta:
        query = query.filter(created_at__gt=datetime.utcnow() - delta)

    sort_column_map = {
        "most_viewed": "view_count",
        "hot": "hot_score"
    }
    sort_column = sort_column_map.get(params.sort, "created_at")

    if params.after_id:
        after_content = await Content.get_or_none(id=params.after_id)
        if after_content:
            after_value = getattr(after_content, sort_column)
            query = query.filter(
                Q(id__not=after_content.id, **{f"{sort_column}__lte": after_value}) |
                Q(**{f"{sort_column}__lt": after_value})
            )

    contents = await query.order_by(f"-{sort_column}", "-id").limit(page_size).all()

    return [
        Headline(
            id=c.id,
            slug=c.slug,
            created_at=c.created_at,
            description=c.description,
            image_id=c.image_id,
            title=c.title
        ) for c in contents
    ]


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
async def article_list(request: Request, params: ContentListParams = Depends()):
    items = await get_next_page(params)
    formatted_items = [format_headline(item) for item in items]
    after_id = formatted_items[-1]['id'] if formatted_items else None
    return render_template("index.html", request=request, items=formatted_items, after_id=after_id)
