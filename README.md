# DEFT: a web-based system for DE-identifying Free Text data in electronic medical records using human in the loop deep learning

DEFT was developed using [Django framework](https://www.djangoproject.com/).

The source code is for the research: [DEFT: a web-based system for DE-identifying Free Text data in electronic medical records using human in the loop deep learning](https://preprints.jmir.org/preprint/46322)

## Dependencies
Python 3.9
Django 4.0.2

## How to quickly run a demo
1. Create a Python virtual environment
2. Download the source code and unzip it
3. Install the dependent libraries
> pip install -r requirements.txt
4. Using the following commands to run the demo.
> python manage.py makemigrations

> python manage.py migrate

> python manage.py createsuperuser

> python manage.py runserver

## Deploy DEFT in Gunicorn
Please refer to the topic: [How to use Django with Gunicorn](https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/gunicorn/)

