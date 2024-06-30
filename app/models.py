from tortoise import fields
from tortoise.models import Model


class Content(Model):
    id = fields.CharField(pk=True, max_length=36)
    slug = fields.CharField(unique=True, max_length=500)
    started_llm_at = fields.DatetimeField(null=True)
    finished_llm_at = fields.DatetimeField(null=True)
    started_images_at = fields.DatetimeField(null=True)
    finished_images_at = fields.DatetimeField(null=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    description = fields.TextField()
    image_id = fields.CharField(max_length=36, null=True)
    title = fields.CharField(max_length=500, index=True)
    flagged = fields.BooleanField(default=False)
    view_count = fields.IntField(default=0)
    hot_score = fields.IntField(default=0)
    markdown = fields.TextField(null=True)
    user_input = fields.TextField()
    content = fields.TextField()


class ImageData(Model):
    id = fields.CharField(pk=True, max_length=36)
    jpeg_data = fields.BinaryField()


class Examples(Model):
    id = fields.CharField(pk=True, max_length=36)
    user_input = fields.TextField()
    title = fields.CharField(max_length=500)
    description = fields.TextField()
    content = fields.TextField()
    new_id = fields.IntField(null=True)


class ContentImage(Model):
    id = fields.CharField(pk=True, max_length=36)
    content_id = fields.CharField(max_length=36)
    prompt = fields.TextField()
    alt_text = fields.CharField(max_length=500)
    created_at = fields.DatetimeField(auto_now_add=True)

