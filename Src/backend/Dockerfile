FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости для PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY ./app ./app

# Создаем не-root пользователя для безопасности
RUN useradd -m -u 1000 fastapi && \
    chown -R fastapi:fastapi /app
USER fastapi

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]