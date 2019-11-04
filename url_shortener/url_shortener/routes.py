from flask import Blueprint, render_template, request, redirect

import short_url

from .extensions import db
from .models import Link

short = Blueprint('short', __name__)

# This method will take the short url from request
# get the corresponding long url from the db table
# redirect to the original url. If fails result into 404
@short.route('/<short_url>')
def redirect_to_url(short_url):
    link = Link.query.filter_by(short_url=short_url).first_or_404()

    link.visits = link.visits + 1
    db.session.commit()
    print(link.original_url)
    return redirect(link.original_url) 

# default route mapping, redirects the user to index page of the application
@short.route('/')
def index():
    return render_template('index.html') 

# This will recieve the POST request from client for adding new long-short url mapping
# First we will check if the same long url already added in the database.
# If present use the same and send it to the user.
# Otherwise go one more level and check if the user has provided a custom URL
# Check for the existence of the custom short url in the table anywhere
# if present let the user know that he/she has to try with a different custom URL
# and redirect to same kind of index page (alreadyexists.html) with error info
# If no custom URL is given by the user, create a new custom URL and associate
# that with the original URL and render the mapping to the user.
@short.route('/add_link', methods=['POST'])
def add_link():
    original_url = request.form['original_url']

    link1 = Link.query.filter_by(original_url=original_url).first()
    if link1:
        return render_template('link_added.html', 
        new_link=link1.short_url, original_url=link1.original_url)    
    
    custom_short_url=request.form['custom_short_url']
    customURLLength = len(custom_short_url)
    if customURLLength>0:
        link2= Link.query.filter_by(short_url=custom_short_url).first()
        if link2:
            return render_template('alreadyexists.html')       
    
    link = Link(original_url=original_url)
    db.session.add(link)
    db.session.commit()
    
    return render_template('link_added.html', 
        new_link=link.short_url, original_url=link.original_url)

@short.route('/stats')
def stats():
    links = Link.query.all()

    return render_template('stats.html', links=links)

# error handling page. For now simple error page with text content in it.
@short.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404