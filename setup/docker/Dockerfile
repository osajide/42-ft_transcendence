FROM debian:bookworm
RUN apt update && apt install nginx -y
COPY nginx.conf /etc/nginx/sites-available/django.conf
RUN ln -s /etc/nginx/sites-available/django.conf /etc/nginx/sites-enabled/django
ENTRYPOINT [ "nginx", "-g", "daemon off;" ]