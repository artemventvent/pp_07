FROM nginx:alpine

# Удаляем конфиг по умолчанию
RUN rm /etc/nginx/conf.d/default.conf

# Копируем наш конфиг
COPY nginx.conf /etc/nginx/conf.d/

# Копируем статические файлы
COPY static /usr/share/nginx/html

# Открываем порт 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]