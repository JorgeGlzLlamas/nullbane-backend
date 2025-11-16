from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as user_router
from app.modules.settings.router import router as settings_router
from app.modules.posts.router import router as posts_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(user_router, prefix="/users", tags=["Usuarios"])
api_router.include_router(settings_router, prefix="/settings", tags=["Configuración"])
api_router.include_router(posts_router, prefix="/posts", tags=["Publicaciones"])
