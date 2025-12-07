# 🐳 Docker Deployment Guide

## Быстрый старт

```bash
# 1. Генерация тестовых данных (10,000 записей)
python generate_mock_data.py

# 2. Запуск в фоновом режиме
docker-compose up -d

# 3. Просмотр логов
docker-compose logs -f

# 4. Остановка
docker-compose down
```

## Доступ к приложению

После успешного запуска:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

## Управление контейнерами

### Просмотр статуса
```bash
docker-compose ps
```

### Перезапуск сервисов
```bash
docker-compose restart
```

### Остановка без удаления
```bash
docker-compose stop
```

### Полная очистка
```bash
docker-compose down -v
```

### Пересборка образов
```bash
docker-compose build --no-cache
docker-compose up -d
```

## Режим разработки

Оба контейнера настроены с volume mounting для live reload:

```yaml
backend:
  volumes:
    - ./backend:/app
    - ./data:/app/data
  command: uvicorn app:app --host 0.0.0.0 --port 8000 --reload

frontend:
  volumes:
    - ./frontend:/app
    - /app/node_modules
  command: npm run dev -- --host
```

Изменения в коде автоматически применяются без перезапуска контейнеров.

## Логи и отладка

### Просмотр логов backend
```bash
docker-compose logs -f backend
```

### Просмотр логов frontend
```bash
docker-compose logs -f frontend
```

### Вход в контейнер backend
```bash
docker-compose exec backend bash
```

### Вход в контейнер frontend
```bash
docker-compose exec frontend sh
```

## Конфигурация портов

Если порты 8000 или 5173 заняты, измените в `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Внешний:Внутренний
  
  frontend:
    ports:
      - "5174:5173"  # Внешний:Внутренний
    environment:
      - VITE_API_URL=http://localhost:8001
```

## Хранение данных

Данные хранятся в CSV файлах и монтируются как volume:

```yaml
volumes:
  - ./data:/app/data
```

Это позволяет:
- ✅ Сохранять данные между перезапусками
- ✅ Редактировать CSV файлы напрямую
- ✅ Генерировать новые данные без пересборки

## Production Deployment

Для production используйте отдельные Dockerfile:

### backend/Dockerfile.prod
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### frontend/Dockerfile.prod
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Troubleshooting

### Проблема: Контейнер не запускается

```bash
# Проверить логи
docker-compose logs backend
docker-compose logs frontend

# Пересоздать контейнеры
docker-compose down
docker-compose up --build
```

### Проблема: Backend недоступен из frontend

Убедитесь, что в frontend используется правильный URL:
```typescript
// frontend/src/App.tsx
const API_URL = 'http://localhost:8000';
```

### Проблема: Изменения не применяются

```bash
# Остановить контейнеры
docker-compose down

# Очистить кэш и пересобрать
docker-compose build --no-cache

# Запустить заново
docker-compose up -d
```

### Проблема: Порты заняты

```bash
# Найти процесс на порту 8000
netstat -ano | findstr :8000

# Убить процесс (Windows)
taskkill /PID <process_id> /F
```

## Мониторинг ресурсов

```bash
# Использование CPU и памяти
docker stats

# Размер образов
docker images

# Очистка неиспользуемых образов
docker system prune -a
```

## Безопасность

Для production:
1. Используйте переменные окружения для конфигурации
2. Не монтируйте директории в режиме записи
3. Ограничьте ресурсы контейнеров:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

## CI/CD Integration

Пример GitHub Actions:

```yaml
name: Docker Build

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build images
        run: docker-compose build
      
      - name: Run tests
        run: docker-compose run backend pytest
```

---

**Готово!** Теперь ваше приложение работает в Docker 🐳
