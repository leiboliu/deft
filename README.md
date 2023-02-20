# DEFT: a web-based system for DE-identifying Free Text data in electronic medical records using human in the loop deep learning

DEFT was developed using [Django framework](https://www.djangoproject.com/).

The source code is for the research: [DEFT: a web-based system for DE-identifying Free Text data in electronic medical records using human in the loop deep learning](https://preprints.jmir.org/preprint/46322)

## Dependencies
Python 3.9
Django 4.0.2

## How to quickly run a demo (development mode)
1. Create a Python (version 3.9.15) virtual environment and activate it
2. Download the demo application (including dummy sample data) [here](https://unsw-my.sharepoint.com/:u:/g/personal/z5250377_ad_unsw_edu_au/ETwJ3GmTGJBEln39Fb79628BtkMvuwjnAGor2IBnuB_WTQ?e=in4tOs) and unzip it into folder "deft_demo"
3. Go into the unzipped folder "deft_demo"
4. Install the dependent libraries
> pip install -r requirements.txt
5. Using the following commands to run the demo.
> python manage.py runserver
6. Access the application via the following URLs:

http://127.0.0.1:8000 (username/password: annotator1/annotator1 or annotator2/annotator2)

http://127.0.0.1:8000/admin (username/password: admin/admin)

## Deploy DEFT in Gunicorn
Please refer to the topic: [How to use Django with Gunicorn](https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/gunicorn/)

