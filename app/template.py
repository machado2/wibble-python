from fastapi import Request
from fastapi.templating import Jinja2Templates
import time

_templates = Jinja2Templates(directory="templates")

_cache_buster = int(time.time())


def render_template(template_name: str, request: Request, **context):
    context["request"] = request
    context["cache_buster"] = _cache_buster
    theme = request.query_params.get("theme") or "style"
    context["css"] = f"/static/{theme}.css"
    context["url_suffix"] = "" if theme == "style" else f"?theme={theme}"
    return _templates.TemplateResponse(template_name, context)
