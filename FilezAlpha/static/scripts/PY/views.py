from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/uploadSuccess')
def home():
	return "<h1>Uploaded your file succefully!</h1>"