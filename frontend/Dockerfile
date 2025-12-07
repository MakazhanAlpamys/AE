FROM node:20-alpine

WORKDIR /app

# Копируем package.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальные файлы
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
