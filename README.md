Егоров Артем Алексеевич

Студент группы - ИС-43

Сроки прохождения практики - 01.12.2025 по 14.12.2025

Тема практики Соадминистрирование баз данных и серверов


-----


# **Система контроля качества металлопроката**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-✔-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Оглавление
- [Краткое описание](#-краткое-описание)
- [🎯 Функциональность](#-функциональность)
- [🏗️ Архитектура](#️-архитектура)
- [📁 Структура проекта](#-структура-проекта)
- [🚀 Запуск](#-запуск)
- [🔧 Установка и настройка](#-установка-и-настройка)
- [📊 Администрирование базы данных](#-администрирование-базы-данных)
- [🔐 Аутентификация и роли](#-аутентификация-и-роли)
- [📡 API Документация](#-api-документация)

## 🎯 Краткое описание

**Система контроля качества металлопроката** — это веб-приложение для автоматизации процесса контроля качества на металлургических предприятиях. Система позволяет отслеживать производственные партии, фиксировать результаты автоматического контроля, выявлять дефекты и управлять пользователями с различными уровнями доступа.

Проект разработан в рамках производственной практики по теме "Соадминистрирование баз данных и серверов" и полностью соответствует требованиям задания, включая:
- ✅ Полный CRUD для всех таблиц БД
- ✅ Администрирование пользователей и ролей
- ✅ Веб-интерфейс с формами для работы с данными
- ✅ Современный стек технологий

## 🎯 Функциональность

### **Основные модули:**
1. **Управление пользователями и ролями**
   - Регистрация и аутентификация пользователей
   - Ролевая модель (админ, менеджер качества, оператор, наблюдатель)
   - Управление правами доступа

2. **Управление производством**
   - Регистрация типов металлопроката
   - Учет производственных партий
   - Отслеживание статусов (в производстве, произведено, отгружено)

3. **Контроль качества**
   - Ведение результатов автоматического контроля
   - Фиксация дефектов с координатами и изображениями
   - Статистика качества по партиям

4. **Аналитика и отчетность**
   - Дашборд с ключевыми метриками
   - Фильтрация и поиск данных
   - История изменений

### **Типы пользователей:**
| Роль | Права | Описание |
|------|-------|----------|
| **Администратор** | Полный доступ ко всем функциям | Настройка системы, управление пользователями |
| **Менеджер качества** | Чтение/запись всех данных, утверждение результатов | Контроль качества, анализ дефектов |
| **Оператор** | Добавление записей, просмотр своих данных | Внесение данных с автоматических систем |
| **Наблюдатель** | Только чтение | Просмотр отчетов и статистики |

## 🏗️ Архитектура

### **Технологический стек:**

```
┌─────────────────────────────────────────────────────────────┐
│                       Веб-браузер                          │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/HTTPS
┌───────────────────────────▼─────────────────────────────────┐
│                    Nginx (Reverse Proxy)                    │
│                    ┌──────────────────┐                    │
│                    │  Статические     │                    │
│                    │  файлы (HTML/    │                    │
│                    │  CSS/JS)         │                    │
│                    └──────────────────┘                    │
└────────────┬────────────────────────────────────────────────┘
             │ API запросы (/api/*)
┌────────────▼────────────────────────────────────────────────┐
│                 FastAPI Backend (Python)                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │   CRUD   │ │  Auth    │ │  Models  │ │  Routes  │     │
│  │ операции │ │ (JWT)    │ │ (SQLA)   │ │ (REST)   │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
└────────────┬────────────────────────────────────────────────┘
             │ SQL запросы
┌────────────▼────────────────────────────────────────────────┐
│                 PostgreSQL Database                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Таблицы: users, roles, batches, inspections, defects│  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### **Контейнеризация:**
```yaml
services:
  postgres:      # База данных PostgreSQL 15
  backend:       # FastAPI приложение на Python
  frontend:      # Nginx с статическими файлами
  pgadmin:       # Веб-интерфейс для администрирования БД
```

## 📁 Структура проекта

```
metal_quality_control/
├── 📁 backend/                    # FastAPI приложение
│   ├── 📁 app/
│   │   ├── 📁 routers/           # Маршруты API
│   │   │   ├── users.py          # Управление пользователями
│   │   │   ├── roles.py          # Управление ролями
│   │   │   ├── batches.py        # Производственные партии
│   │   │   ├── inspections.py    # Результаты контроля
│   │   │   └── defects.py        # Дефекты
│   │   ├── main.py              # Точка входа FastAPI
│   │   ├── models.py            # SQLAlchemy модели
│   │   ├── schemas.py           # Pydantic схемы
│   │   ├── crud.py              # CRUD операции
│   │   ├── auth.py              # Аутентификация
│   │   └── database.py          # Подключение к БД
│   ├── requirements.txt         # Зависимости Python
│   └── Dockerfile              # Docker образ для бэкенда
│
├── 📁 frontend/                  # Веб-интерфейс
│   ├── 📁 static/
│   │   ├── index.html          # Главная страница
│   │   ├── style.css           # Стили CSS
│   │   └── script.js           # JavaScript логика
│   ├── nginx.conf              # Конфигурация Nginx
│   └── Dockerfile              # Docker образ для фронтенда
│
├── 📁 postgres/                  # Конфигурация БД
│   ├── init-db.sql            # SQL скрипт инициализации
│   └── pg_hba.conf            # Настройки безопасности
│
├── docker-compose.yml          # Docker Compose конфигурация
├── .env.example               # Шаблон переменных окружения
└── README.md                  # Эта документация

```

### **Детальное описание ключевых файлов:**

#### **1. База данных (`postgres/init-db.sql`)**
```sql
-- Основные таблицы:
-- 1. users - Пользователи системы
-- 2. roles - Роли и права доступа
-- 3. product_types - Типы металлопроката
-- 4. production_batches - Производственные партии
-- 5. inspection_results - Результаты контроля
-- 6. defect_types - Типы дефектов
-- 7. defect_details - Детали дефектов
-- 8. inspection_points - Контрольные точки

-- Особенности:
-- • JSONB поля для гибкого хранения данных
-- • Триггеры для автоматического обновления
-- • Индексы для оптимизации запросов
-- • Начальные тестовые данные
```

#### **2. Docker Compose (`docker-compose.yml`)**
```yaml
version: '3.8'
services:
  postgres:    # База данных на порту 5432
  backend:     # API на порту 8000 (внутренний)
  frontend:    # Веб-интерфейс на порту 80
  pgadmin:     # Админка БД на порту 5050
```

#### **3. Модели данных (`backend/app/models.py`)**
```python
# Основные сущности:
class ProductionBatch(Base):     # Производственная партия
class InspectionResult(Base):    # Результат контроля
class DefectDetail(Base):        # Детализация дефекта
class User(Base):               # Пользователь
class Role(Base):               # Роль
```

## 🚀 Запуск

### **Требования:**
- [Docker](https://docs.docker.com/get-docker/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) 2.0+
- 4 GB свободной памяти
- Порты: 80, 5432, 8000, 5050

### **Запуск за 5 минут:**

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/artemventvent/pp_07.git
cd pp_07
```

2. **Создайте файл окружения:**
```bash
cp .env.example .env
# Отредактируйте .env при необходимости
```

3. **Запустите систему:**
```bash
docker-compose up --build
```

4. **Откройте в браузере:**
- 🌐 Веб-интерфейс: http://localhost
- 📚 Документация API: http://localhost/api/docs
- 🗄️ Админка БД: http://localhost:5050

5. **Войдите в систему:**
- **Логин:** `admin_user`
- **Пароль:** `password123`

## 🔧 Установка и настройка

### **1. Ручная установка (без Docker)**

#### **Требования:**
- Python 3.11+
- PostgreSQL 15+
- Node.js (опционально, для сборки фронтенда)

#### **Шаги установки:**

**Бэкенд:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt

# Настройка переменных окружения
export DATABASE_URL=postgresql://user:pass@localhost/metal_quality_control
export SECRET_KEY=your-secret-key

# Запуск миграций (если используете Alembic)
alembic upgrade head

# Запуск сервера
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Фронтенд:**
```bash
cd frontend
# Установите Nginx или используйте любой веб-сервер
# Скопируйте файлы в директорию сервера
```

**База данных:**
```bash
# Создание БД и пользователя
sudo -u postgres psql
CREATE DATABASE metal_quality_control;
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE metal_quality_control TO app_user;

# Инициализация схемы
psql -U postgres -d metal_quality_control -f postgres/init-db.sql
```

### **2. Конфигурация окружения**

Создайте файл `.env` в корне проекта:

```env
# База данных
DATABASE_URL=postgresql://postgres:postgres_password@postgres:5432/metal_quality_control
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_password
POSTGRES_DB=metal_quality_control

# Безопасность
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Домен
FRONTEND_URL=http://localhost
API_URL=http://localhost:8000

# pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin
```

### **3. Настройка SSL/HTTPS**

Для продакшн окружения добавьте SSL:

```nginx
# frontend/nginx.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    
    # ... остальная конфигурация
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 📊 Администрирование базы данных

### **Структура базы данных:**

```sql
-- Основные связи:
production_batches → product_types
inspection_results → production_batches
defect_details → inspection_results + defect_types
users → roles
```

### **Миграции:**

Проект использует Alembic для управления миграциями:

```bash
# Инициализация Alembic
alembic init alembic

# Создание миграции
alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

### **Резервное копирование:**

```bash
# Экспорт данных
docker-compose exec postgres pg_dump -U postgres metal_quality_control > backup.sql

# Импорт данных
docker-compose exec -T postgres psql -U postgres metal_quality_control < backup.sql
```

### **Оптимизация производительности:**

```sql
-- Рекомендуемые индексы
CREATE INDEX idx_inspections_batch_date ON inspection_results(batch_id, inspection_time DESC);
CREATE INDEX idx_defects_severity_date ON defect_details(severity DESC, created_at DESC);

-- Статистика использования
SELECT schemaname, tablename, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
FROM pg_stat_user_tables;
```

## 🔐 Аутентификация и роли

### **Система аутентификации:**

- **JWT токены** с временем жизни 30 минут
- **Хеширование паролей** через bcrypt
- **Ролевая модель** с гибкими правами

### **Пример работы с правами:**

```python
# Проверка прав в роутерах
if not (current_user.role and current_user.role.permissions.get("admin")):
    raise HTTPException(status_code=403, detail="Недостаточно прав")

# Проверка в бизнес-логике
def can_user_delete(user, entity):
    if user.role.permissions.get("admin"):
        return True
    if user.role.permissions.get("delete") and entity.created_by == user.id:
        return True
    return False
```

### **Добавление нового типа роли:**

1. Добавить запись в таблицу `roles`
2. Настроить права в поле `permissions` (JSON)
3. Обновить фронтенд для отображения новой роли

```sql
INSERT INTO roles (role_name, description, permissions) VALUES
('technician', 'Техник', '{"read": true, "write": true, "delete": false, "admin": false}');
```

## 📡 API Документация

### **Базовый URL:** `http://localhost:8000/api`

### **Основные endpoint-ы:**

#### **Аутентификация:**
```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=admin_user&password=password123
```

#### **Пользователи:**
```http
GET    /users          # Список пользователей (только админ)
POST   /users          # Создание пользователя
GET    /users/{id}     # Получение пользователя
PUT    /users/{id}     # Обновление пользователя
DELETE /users/{id}     # Удаление пользователя
```

#### **Производственные партии:**
```http
GET    /batches?status=в_производстве&limit=100
POST   /batches
GET    /batches/{id}
PUT    /batches/{id}
DELETE /batches/{id}
```

#### **Результаты контроля:**
```http
GET    /inspections?batch_id=1&verdict=соответствует
POST   /inspections
GET    /inspections/{id}
PUT    /inspections/{id}
DELETE /inspections/{id}
```

### **Примеры запросов:**

```bash
# Получение токена
curl -X POST "http://localhost:8000/api/auth/token" \
     -d "username=admin_user&password=password123"

# Создание партии
curl -X POST "http://localhost:8000/api/batches" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "batch_number": "BATCH-2024-06-001",
       "product_type_id": 1,
       "production_date": "2024-06-15",
       "status": "в производстве"
     }'

# Получение статистики
curl -X GET "http://localhost:8000/api/inspections/stats?start_date=2024-01-01&end_date=2024-12-31" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### **Ответы API:**

**Успешный ответ:**
```json
{
  "id": 1,
  "batch_number": "BATCH-2024-06-001",
  "status": "в производстве",
  "created_at": "2024-06-15T10:30:00Z"
}
```

**Ошибка:**
```json
{
  "detail": "Пользователь не найден"
}
```

**Коды состояния:**
- `200` - Успех
- `201` - Создано
- `400` - Неверный запрос
- `401` - Не авторизован
- `403` - Запрещено
- `404` - Не найдено
- `422` - Ошибка валидации
- `500` - Ошибка сервера

