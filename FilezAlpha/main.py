from flask import Flask, Blueprint, render_template, request, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql import func
import os
from os import path
from werkzeug.security import generate_password_hash, check_password_hash
import time
from flask_login import login_user, login_required, logout_user, current_user, LoginManager

db = SQLAlchemy()
DB_NAME = "databaseUsers.db"


	# f'sqlite:///{DB_NAME}'


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dhasjdh dhasjdhd'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
db.init_app(app)


def databaseCreation(app):
	if not path.exists('/instance/databaseUsers.db'):
		with app.app_context():
			db.create_all()
			#db.drop_all()
			print('Database Created!')

#Database Models
class Note(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	data = db.Column(db.String(10000))
	date = db.Column(db.DateTime(timezone=True), default=func.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(150), unique=True)
	password = db.Column(db.String(150))
	notes = db.relationship('Note')

databaseCreation(app)

login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.route('/')
def home():
	return render_template('index.html', user=current_user)

@app.route('/info')
def privacy():
	return "<h1>Working on it... {{userInfos.username}}</h1>"

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		


		user = User.query.filter_by(email=email).first()
		if user:
			if check_password_hash(user.password, password):
				flash('Autenticato con successo! (ATTENZIONE: Il sito è ancora in costruzione!)', category='success')
				login_user(user, remember=True)
				return redirect('/')
				 
			else:
				flash('Password non corretta.', category='error')
		else:
			flash('Utente inesistente.', category='error')

	return render_template('login.html', user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		passwordConfirm = request.form.get('passwordConfirm')
		#username = email.split("@")[0]
		#print (username)
		
		user = User.query.filter_by(email=email).first()
		
		if user:
			flash('Un account con questa email esiste già!', category='error')
		elif password != passwordConfirm:
			print('Password non corrispondono')
			flash('Le due password non corrispondono!', category='error')
		elif len(password) < 7:
			flash('La password deve contenere almeno 7 caratteri', category='error')
		else:
			new_user = User(email=email, password=generate_password_hash(password, method='sha256'))
			db.session.add(new_user)
			db.session.commit()
			login_user(user, remember=True)
			flash('Account creato!', category='success')
			return redirect('/', user=current_user)

		

	return render_template('register.html')

@app.route('/coming-soon')
def comingsoon():
	return "Coming soon! © Filez 2023 LeoTecno"

@app.route('/trolling-time')
def trollingtime():
	print("+ un rickrollato")
	time.sleep(3)
	return redirect('https://git.leotecno.tk')

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect('/login')

@app.route('/upload')
@login_required
def upload():
	return "Working on it..."

@app.route('/myFiles')
@login_required
def myfiles():
	return "Working on it..."





if __name__ == '__main__':
	app.run(host='127.0.0.1', port=80, debug=True)

