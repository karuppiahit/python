import string
from datetime import datetime
from random import choices
from flask import request

from .extensions import db 

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(512))
    short_url = db.Column(db.String(512), unique=True)
    visits = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.now)
    # Already we had verified in the route level whether the client 
    # provided custom short URL is not present in DB.
    # Here we will check if there is a custom URL provided by the user.
    # If so use it. Other generate a random 6 letter (char+digit) and use that.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)     
        custom_short_url=request.form['custom_short_url']         
        if len(custom_short_url)>0:
            self.short_url = custom_short_url
        else:
            self.short_url = self.generate_short_link()

    # will be called only in case the provided original url is fresh
    # and also the client has not provided a custom short url
    # After generation we will check whether the random generated string is already present 
    # in DB. if so recursively call the same method until generate a unique combination
    # of short URL.   
    def generate_short_link(self):
        characters = string.digits + string.ascii_letters
        short_url = ''.join(choices(characters, k=6))
        
        link = self.query.filter_by(short_url=short_url).first()

        if link:
            return self.generate_short_link()
        
        return short_url

    