from mongoengine import *

class DJ(Document):
    name = StringField(required=True)
    bio = StringField()
    votes = IntField(default=0)

class Voter(Document):
    name = StringField(required=True)
    email = StringField(required=True)