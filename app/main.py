from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, usuarios, mascotas, veterinarias, profesionales, citas_veterinarias, recordatorios, medicamentos, vacunas, carrito, pedidos, productos  # Importamos el router de recordatorios

app = FastAPI(
    title="PeludOS API",
    description="API para la plataforma de cuidado de mascotas",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(mascotas.router)
app.include_router(veterinarias.router)
app.include_router(profesionales.router)
app.include_router(citas_veterinarias.router)
app.include_router(recordatorios.router)
app.include_router(medicamentos.router)  # Incluimos el router de medicamentos
app.include_router(vacunas.router)  # Incluimos el router de vacunas
app.include_router(carrito.router)  # Incluimos el router de carrito
app.include_router(pedidos.router)  # Incluimos el router de pedidos
app.include_router(productos.router)  # Incluimos el router de productos

def health_check():
    """
    Endpoint simple para verificar que la API está corriendo
    y respondiendo correctamente.
    """
    return {"status": "ok", "app": "PeludOS API"}