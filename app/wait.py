from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.models import Content
from app.template import render_template

router = APIRouter()

background_ids = {}


@router.get('/{identifier}')
async def get_wait(request: Request, identifier: str):
    if identifier in background_ids:
        return render_template("wait.html", request, identifier=identifier)
    content = await Content.get_or_none(id=identifier)
    if content:
        return RedirectResponse(url=f"/content/{content.slug}", status_code=303)
    else:
        return RedirectResponse(url="/", status_code=303)
