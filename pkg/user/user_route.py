from flask import render_template, url_for,request,redirect

from pkg.user import userobj

@userobj.route('/')
def home():
    return "This is the user page"