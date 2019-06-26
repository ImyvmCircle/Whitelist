from tortoise import Tortoise

from settings import db_settings


async def init():
    config = {
        'connections': {
            'default': db_settings
        },
        'apps': {
            'models': {
                'models': ['orm.models']
            }
        }
    }

    await Tortoise.init(config=config)
    await Tortoise.generate_schemas()


async def close():
    await Tortoise.close_connections()
