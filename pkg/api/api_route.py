from flask import render_template, url_for,request,redirect

from pkg.api import apiobj

@apiobj.route('/')
def api_home():
    return "This is the API's home page"