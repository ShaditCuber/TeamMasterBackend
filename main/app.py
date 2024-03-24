import platform
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum

from routes import (
    groups,
    images
)

from auth.jwt_bearer import JWTBearer  # -> En caso de autenticacion

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MACOS = platform.system() == "Darwin"

app = FastAPI()


tags_metadata = [
    {
        "name": "Ejemplo",
        "description": "Ejemplo",
    }
]

origins = [
    "http://localhost:5173",  # Para pruebas en local
]


app = FastAPI(
    openapi_tags=tags_metadata,
    title="Ejemplo",
    description="Ejemplo",
    version="1.0.0",
)


# Incluir los routers
app.include_router(
    groups.router,
    prefix="/api/v1/groups",
    tags=["Generate Groups"],
    # dependencies=[Depends(JWTBearer())],  # -> Si se requiere autenticación
)

app.include_router(
    images.router,
    prefix="/api/v1/images",
    tags=["Images"],
    # dependencies=[Depends(JWTBearer())],  # -> Si se requiere autenticación
)

# Incluir el middleware para CORS en caso de ser necesario
if IS_WINDOWS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# En caso de existir un error
@app.exception_handler(Exception)
async def validation_exception_handler(request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )


# Iniciar la aplicación
handler = Mangum(app)
