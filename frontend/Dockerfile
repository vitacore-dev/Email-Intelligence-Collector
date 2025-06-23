FROM node:18-alpine

WORKDIR /app

# Копирование package.json и установка зависимостей
COPY package*.json ./
COPY pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

# Копирование исходного кода
COPY . .

# Переменные окружения
ENV REACT_APP_API_URL=http://localhost:8000

# Порт приложения
EXPOSE 3000

# Команда запуска в режиме разработки
CMD ["pnpm", "run", "dev", "--host"]

