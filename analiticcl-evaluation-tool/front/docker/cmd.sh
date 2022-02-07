mkdir -p /nginx_conf && \
echo "> substituting environment variables in /tmp/nginx.conf.tpl:" && \
/usr/local/bin/envsubst -no-unset -no-empty -i /tmp/nginx.conf.tpl -o /nginx_conf/nginx.conf && \
echo && \
echo "> testing /nginx_conf/nginx.conf:" && \
nginx -t -c /nginx_conf/nginx.conf && \
echo && \
echo "> starting nginx:" && \
nginx -c /nginx_conf/nginx.conf -g 'daemon off;'
