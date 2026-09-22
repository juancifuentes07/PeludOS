from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# Motor de conexión a la base de datos
engine = create_engine(settings.DATABASE_URL)

# Fábrica de sesiones (cada request abrirá su propia sesión)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la que heredarán todos los modelos (usuarios, mascotas, etc.)
Base = declarative_base()


def get_db():
    """
    Dependencia de FastAPI: entrega una sesión de base de datos por request
    y la cierra automáticamente al terminar, incluso si hay un error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()