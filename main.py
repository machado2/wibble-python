import os

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.article_list import router as article_list_router
from app.get_image import router as get_image_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(article_list_router, prefix='')
app.include_router(get_image_router, prefix='')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)