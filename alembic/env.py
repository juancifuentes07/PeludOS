from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.config import settings
from app.database import Base

from app.models.usuario import Usuario  # Importamos los modelos para que Alembic los detecte al autogenerar migraciones.
from app.models.mascota import Mascota  # Importamos los modelos para que Alembic los detecte al autogenerar migraciones.   
from app.models.veterinaria import Veterinaria  # Importamos los modelos para que Alembic los detecte al autogenerar migraciones.
from app.models.profesional import Profesional  # Importamos los modelos para que Alembic los detecte al autogenerar migraciones.
from app.models.cita_veterinaria import CitaVeterinaria  # Importamos los modelos para que Alembic los detecte al autogenerar migraciones.

# Importamos los modelos para que Alembic los detecte al autogenerar migraciones.
# Por ahora no hay ninguno; los iremos agregando aquí en cada fase.
from app.models.usuario import Usuario

# Configuración de logging de Alembic
config = context.config

# Inyectamos la URL real de la base de datos desde nuestro settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata usada para el autogenerado de migraciones
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()