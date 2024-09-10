from django.db import models
from db_connect import db

# Create your models here.
traffic_true_db = db['traffic_true']
traffic_false_db = db['traffic_false']

jamming_db = db['jamming']
#jamming_false_db = db['jamming_false']