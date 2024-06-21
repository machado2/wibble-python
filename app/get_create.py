from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse

from app.template import render_template

router = APIRouter()


@router.get('/', response_class=HTMLResponse)
async def get_create(request: Request):
    return render_template("create.html", request)
