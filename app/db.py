from tortoise import Tortoise

from settings import TORTOISE_ORM


async def init():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def close():
    await Tortoise.close_connections()
