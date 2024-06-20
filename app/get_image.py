from fastapi import APIRouter, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_session
from app.models import ImageData

router = APIRouter()


@router.get('/image/{image_id}', response_class=Response, responses={200: {"content": {"image/jpeg": {}}}})
async def get_image(image_id: str, db: AsyncSession = Depends(get_session)):
    # noinspection PyTypeChecker
    query = select(ImageData).where(ImageData.id == image_id)
    result = await db.execute(query)
    image = result.scalar_one_or_none()
    if image is None:
        raise Exception('NotFound')
    return Response(content=image.jpeg_data, media_type='image/jpeg')
