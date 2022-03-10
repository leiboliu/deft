from deft.settings.common import *

# production settings to
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['0.0.0.0', 'localhost']

# Model will be retrained when completed document number increase to threshold
MODEL_RETRAIN_THRESHOLD = 100
# The ratios to split the data to train/val/test
MODEL_TRAINING_DATA_RATIOS = '0.8:0.1:0.1'
# if start auto training
AUTO_MODEL_RETRAINING = False
# Retraining check interval
RETRAINING_CHECK_INTERVAL = 36000

# de-id method: replace with surrogates or randomly generated words

# session
SESSION_COOKIE_AGE=10
SESSION_EXPIRE_AT_BROWSER_CLOSE=True
SESSION_SAVE_EVERY_REQUEST=True
