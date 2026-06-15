#!/usr/bin/env sh
set -e

# Домен и почта берутся из .env (рядом). Можно переопределить флагом --staging.
DOMAIN="${DOMAIN:-demoplast.example}"
EMAIL="${CERTBOT_EMAIL:-admin@demoplast.example}"
COMPOSE="docker compose -f compose.prod.yaml"
STAGING=""

if [ "$1" = "--staging" ]; then
  STAGING="--staging"
  echo ">>> STAGING режим (тестовый серт Let's Encrypt)"
fi

CERT_PATH="/etc/letsencrypt/live/$DOMAIN"

echo ">>> 1/4 Временный самоподписанный серт (чтобы nginx смог стартовать)"
$COMPOSE run --rm --entrypoint "\
  sh -c 'mkdir -p $CERT_PATH && \
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout $CERT_PATH/privkey.pem \
    -out $CERT_PATH/fullchain.pem \
    -subj /CN=localhost'" certbot

echo ">>> 2/4 Поднимаю nginx с временным сертом"
$COMPOSE up -d nginx

echo ">>> 3/4 Удаляю временный серт и запрашиваю настоящий"
$COMPOSE run --rm --entrypoint "\
  sh -c 'rm -rf $CERT_PATH /etc/letsencrypt/archive/$DOMAIN /etc/letsencrypt/renewal/$DOMAIN.conf; \
  certbot certonly --webroot -w /var/www/certbot \
    $STAGING -d $DOMAIN \
    --email $EMAIL --agree-tos --no-eff-email --non-interactive'" certbot

echo ">>> 4/4 Перезагружаю nginx с настоящим сертом"
$COMPOSE exec nginx nginx -s reload

echo ">>> Готово. https://$DOMAIN"
