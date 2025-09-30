#!/bin/bash

# Solo crear el proyecto si no existe manage.py
if [ ! -f "/app/backend/manage.py" ]; then
  echo "🛠️ Creando proyecto Django..."
  django-admin startproject primer_parcial /app/backend
  echo "✅ Proyecto creado."
fi

cd /app/backend

# Esperar a que la base de datos esté lista
echo "⏳ Esperando a que PostgreSQL esté listo..."
until python -c "import psycopg2; psycopg2.connect(dbname='${POSTGRES_DB}', user='${POSTGRES_USER}', password='${POSTGRES_PASSWORD}', host='${POSTGRES_HOST}', port='${POSTGRES_PORT}')" 2>/dev/null; do
  echo "PostgreSQL no está listo, esperando..."
  sleep 2
done
echo "✅ PostgreSQL está listo."

# Esperar a que Redis esté listo
echo "⏳ Esperando a que Redis esté listo..."
until python -c "import redis; r = redis.Redis(host='${REDIS_HOST}', port=${REDIS_PORT}); r.ping()" 2>/dev/null; do
  echo "Redis no está listo, esperando..."
  sleep 2
done
echo "✅ Redis está listo."

# Ejecutar makemigrations
echo "🔄 Ejecutando makemigrations..."
python manage.py makemigrations

# Ejecutar migrate
echo "🔄 Ejecutando migrate..."
python manage.py migrate --noinput

# Crear superusuario automáticamente si no existe
if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists())" | grep -q True; then
  echo "🛠️ Creando superusuario..."
  python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser(
    "${DJANGO_SUPERUSER_USERNAME}",
    "${DJANGO_SUPERUSER_EMAIL}",
    "${DJANGO_SUPERUSER_PASSWORD}"
)
END
else
  echo "✅ Superusuario ya existe."
fi

# Iniciar el servidor con Daphne (para WebSockets)
echo "🚀 Iniciando Django con Daphne..."
daphne -b 0.0.0.0 -p 8000 primer_parcial.asgi:application

# Si prefieres runserver (sin WebSockets en producción):
# python manage.py runserver 0.0.0.0:8000