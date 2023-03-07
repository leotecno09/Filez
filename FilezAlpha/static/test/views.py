from flask import Blueprint, render_template

views = Blueprint('views', __name__,template_folder='/assets/pages/')

@views.route('/')
def home():
	return render_template('main.html')