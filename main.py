import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.article_list import router as article_list_router
from app.create import router as get_create_router
from app.db import close as close_db
from app.db import init as init_db
from app.get_content import router as get_content_router
from app.get_image import router as get_image_router
from app.wait import router as wait_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(article_list_router, prefix='')
app.include_router(get_image_router, prefix='/image')
app.include_router(get_content_router, prefix='/content')
app.include_router(get_create_router, prefix='/create')
app.include_router(wait_router, prefix='/wait')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
