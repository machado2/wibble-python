from fastapi import APIRouter, Response, HTTPException

from app.models import ImageData

router = APIRouter()


@router.get('/{image_id}', response_class=Response, responses={200: {"content": {"image/jpeg": {}}}})
async def get_image(image_id: str):
    image = await ImageData.filter(id=image_id).first()
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return Response(content=image.jpeg_data, media_type='image/jpeg')
