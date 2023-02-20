from deft.settings.common import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(gb8a%_zsod)!+^74oocn+hmo7urrq1f1x!)o9y_fway#46$o+'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Model will be retrained when completed document number increase to threshold
MODEL_RETRAIN_THRESHOLD = 10
# The ratios to split the data to train/val/test
MODEL_TRAINING_DATA_RATIOS = '0.8:0.1:0.1'
# if start auto training
AUTO_MODEL_RETRAINING = True
# Retraining check interval
RETRAINING_CHECK_INTERVAL = 600

# Auto import dataset
AUTO_IMPORT_DATASETS = True
AUTO_IMPORT_CHECK_INTERVAL = 60

# de-id method: replace with surrogates or randomly generated words

# session
SESSION_SAVE_EVERY_REQUEST=True
SESSION_EXPIRE_AT_BROWSER_CLOSE=True
SESSION_COOKIE_AGE=900
