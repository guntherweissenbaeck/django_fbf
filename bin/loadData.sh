#/bin/bash
# docker-compose exec web python manage.py loaddata fixtures/defaultUser
# docker-compose exec web python manage.py loaddata fixtures/bird
# docker-compose exec web python manage.py loaddata fixtures/birdCircumstance
# docker-compose exec web python manage.py loaddata fixtures/birdStatus

docker-compose exec web python manage.py loaddata fixtures/{bird.json,birdCircumstance,birdStatus.json,defaultUser.json}
