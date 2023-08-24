#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DBHOST $DBPORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py migrate
python manage.py loaddata fixtures/init.json
python manage.py loaddata fixtures/auth_fixture.json
python manage.py loaddata fixtures/fixture.json
# python manage.py loaddata fixtures/prod_auth_backup.json
# python manage.py loaddata fixtures/prod_backup.json

exec "$@"
