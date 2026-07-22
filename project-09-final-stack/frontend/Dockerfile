FROM nginx:1.30.4-alpine3.24

COPY nginx-main.conf /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY site/ /usr/share/nginx/html/

RUN chown -R 101:101 \
    /usr/share/nginx/html \
    /etc/nginx/nginx.conf \
    /etc/nginx/conf.d

USER 101:101

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
