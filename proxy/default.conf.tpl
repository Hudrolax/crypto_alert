server {
  listen ${LISTEN_PORT};

  location /static {
    alias /vol/static;
  }

  location / {
    uwsgi_pass            ${APP_HOST}:${APP_PORT}; 
    include               /etc/nginx/uwsgi_params;
    client_max_body_size  10M;
  }

  location /${APP_URL}flower {
    proxy_pass http://flower:5555/${APP_URL}flower;
    proxy_buffering off;
  }

}
