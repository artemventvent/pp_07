from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud, auth
from .database import engine, get_db
from .config import settings

# Создаем таблицы в БД (в продакшене используйте Alembic миграции)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Metal Quality Control API",
    description="API для системы контроля качества металлопроката",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://frontend", settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 схема для токенов
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


# Зависимость для получения текущего пользователя
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = auth.verify_token(token, credentials_exception)
    user = crud.get_user_by_username(db, username=token_data.username)
    
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user


# Импортируем роутеры
from .routers import users, roles, product_types, batches, inspections, defects, auth as auth_router

# Подключаем роутеры
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"], dependencies=[Depends(get_current_user)])
app.include_router(roles.router, prefix="/api/roles", tags=["Roles"], dependencies=[Depends(get_current_user)])
app.include_router(product_types.router, prefix="/api/product-types", tags=["Product Types"], dependencies=[Depends(get_current_user)])
app.include_router(batches.router, prefix="/api/batches", tags=["Batches"], dependencies=[Depends(get_current_user)])
app.include_router(inspections.router, prefix="/api/inspections", tags=["Inspections"], dependencies=[Depends(get_current_user)])
app.include_router(defects.router, prefix="/api/defects", tags=["Defects"], dependencies=[Depends(get_current_user)])


@app.get("/")
async def root():
    return {
        "message": "Metal Quality Control API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Проверка здоровья приложения и подключения к БД"""
    try:
        # Простой запрос к БД для проверки подключения
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)