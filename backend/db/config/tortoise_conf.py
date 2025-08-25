# tortoise_conf.py
from backend.db.config.config import settings

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host":     settings.mysql.host,
                "port":     settings.mysql.port,
                "user":     settings.mysql.user,
                "password": settings.mysql.password,
                "database": settings.mysql.database,
                "charset":  settings.mysql.charset,
                "minsize":  settings.mysql.pool_size,
                "maxsize":  settings.mysql.max_pool_size,
                "echo":     settings.mysql.echo,
                "pool_recycle": settings.mysql.pool_recycle,
            },
        }
    },
    "apps": {
        "models": {
            "models": ["backend.db.models.entity"],
            "default_connection": "default",
        }
    },
}