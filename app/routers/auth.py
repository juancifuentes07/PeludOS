from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, Token
from app.crud.usuario import get_usuario_by_correo, create_usuario
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario.
    Valida que el correo no esté ya registrado antes de crear.
    """
    usuario_existente = get_usuario_by_correo(db, usuario_data.correo_electronico)
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario registrado con este correo electrónico",
        )
    return create_usuario(db, usuario_data)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autentica a un usuario y devuelve un token JWT.
    Usa OAuth2PasswordRequestForm: espera 'username' y 'password' (form-data),
    donde 'username' será el correo electrónico.
    """
    usuario = get_usuario_by_correo(db, form_data.username)

    if not usuario or not verify_password(form_data.password, usuario.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    access_token = create_access_token(data={"sub": str(usuario.id_usuario)})
    return Token(access_token=access_token)