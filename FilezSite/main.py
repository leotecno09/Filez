from flask import Flask, Blueprint, render_template, request, flash, redirect, session, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql import func
import os
from os import path
from werkzeug.security import generate_password_hash, check_password_hash
import time
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from datetime import timedelta
import random
import string

db = SQLAlchemy()
DB_NAME = "databaseUsers.db"
DB_FILES_NAME = "databaseFiles.db"

blog = Blueprint('blog', __name__)



	# f'sqlite:///{DB_NAME}'


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dhasjdh dhasjdhd'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SQLALCHEMY_BINDS'] = {
	'files': f'sqlite:///{DB_FILES_NAME}'
}
#app.config['FILES_UPLOADS'] = "//RASPBERRYPI/Leo/Workstation/FilezAlpha/static/users/uploaded_files/"
db.init_app(app)


def databaseCreation(app):
	if not path.exists('/instance/databaseUsers.db'):
		with app.app_context():
			db.create_all()
			#db.drop_all()
			#print('Database Created!')


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

class Files(db.Model):
	__bind_key__ = 'files'
	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(100))
	uploaduser = db.Column(db.String(100))
	filedir = db.Column(db.String(100))
	shared = db.Column(db.String(100))
	shareduser = db.Column(db.String(100))
	dateupload = db.Column(db.DateTime(timezone=True), default=func.now())
	securitykey = db.Column(db.String(100))
	filecode = db.Column(db.String(100))

databaseCreation(app)

login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)
login_manager.login_message = "Devi essere autenticato per accedere a questa pagina!"
login_manager.login_message_category = "error"
login_manager.needs_refresh_message = "Sessione scaduta! Perfavore esegui nuovamente l'accesso."
login_manager.needs_refresh_message_category = "error"

@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.route('/', methods=['GET', 'POST'])
def home():
	return render_template('home.html', user=current_user, title="Filez | Home")
	#return render_template('index.html', user=current_user)

#@app.route('/oldHome')
#def realHome():
#	return render_template('index_old.html', user=current_user)

@app.route('/info')
def privacy():
	return redirect(url_for('infos'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		username = email.split("@")[0]
		


		user = User.query.filter_by(email=email).first()
		if user:
			if check_password_hash(user.password, password):
				flash('Autenticato con successo!', category='success')
				login_user(user, remember=True)
				username = email.split("@")[0]
				session['usernameglobale'] = username
				return redirect(url_for('home'))
				 
			else:
				flash('Password non corretta.', category='error')
		else:
			flash('Utente inesistente o email errata.', category='error')
	#else:
	#	flash('Il server non è in grado di gestire la richiesta in questo momento.')

	return render_template('login_prox.html', user=current_user, navbar='withhome', title="FilEZ | Login")



@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		passwordConfirm = request.form.get('passwordConfirm')
		username = email.split("@")[0]
		
		user = User.query.filter_by(email=email).first()
		
		if user:
			flash('Un account con questa email esiste già!', category='error')
		elif password != passwordConfirm:
			#print('Password non corrispondono')
			flash('Le due password non corrispondono!', category='error')
		elif len(password) < 7:
			flash('La password deve contenere almeno 7 caratteri', category='error')
		else:
			new_user = User(email=email, password=generate_password_hash(password, method='sha256'))
			db.session.add(new_user)
			db.session.commit()
			flash('Account creato!', category='success')
			user_folder = os.path.join('//RASPBERRYPI/Leo/Workstation/FilezAlpha/static/users/', username)
			os.mkdir(user_folder)
			login_user(new_user, remember=True)
			session['usernameglobale'] = username
			session['emailglobale'] = email
			return redirect(url_for('home'))

		

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
	flash("Logout effettuato con successo!")
	return redirect('/')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
	usernameglobale = session.get('usernameglobale', None)
	if request.method == 'POST':
		if request.files:
			file = request.files["file"]
			if file.filename == '':
				flash("Seleziona un file.", category="error")
			
			else:

				user_folder = os.path.join('//RASPBERRYPI/Leo/Workstation/FilezAlpha/static/users/', usernameglobale, './uploaded')
				ifExist = os.path.exists(user_folder)
				if ifExist == False:
					os.mkdir(user_folder)
					print ("Folder created!")
				else:
					pass
					print ("Folder creation passed!")
				app.config["UPLOADED_FILE_FOLDER_FOR_USER"] = user_folder

				string_length = 8
				id = ''.join([random.choice('0123456789') for n in range(string_length)])
				print (id)
				securitykey = ''.join(random.choice(string.ascii_letters) for i in range(10))
				filedirdb = user_folder + '/' + file.filename
				fileExists = os.path.exists(filedirdb)

				if fileExists == True:
					flash ("Hai già caricato un file con questo nome!", category="error")
					return redirect('/')
			
				else:
					shared = request.form.getlist('shared')
					print (shared)
					file.save(os.path.join(app.config["UPLOADED_FILE_FOLDER_FOR_USER"], file.filename))
					thingstoadd = Files(id=id, filename=file.filename, uploaduser=usernameglobale, filedir=filedirdb, shared='False', shareduser="None", securitykey=securitykey)
					db.session.add(thingstoadd)
					db.session.commit()

					flash("File caricato!")
					print(file.filename)
			#return render_template(url_for('yourfile.html', filename=file.filename))
		
		else:
			flash("C'è stato un errore, riprova.", category="error")



	return redirect('/')

@app.route('/<e>')
@app.errorhandler(404)
def page_not_found(e):
	return render_template('general-error.html', resourcenotfound=e, errorcode='404')

@app.errorhandler(403)
def not_enough_perms(e):
	return render_template('general-error.html', errorcode='403')

@app.route('/account/profile')
@login_required
def myid():
	username = session.get("usernameglobale")
	return "Autenticato come %s" % username

@app.route('/UserDashboard', methods=['GET', 'POST'])
@login_required
def UserDashboard():
	username = session.get("usernameglobale")
	return render_template('userdashboard.html', name=username, files="100000", sharedfiles="3", archivesize="8GB")

@app.before_request
def before_request():
	session.permanent = True
	app.permanent_session_lifetime = timedelta(minutes=1440)
	session.modified = True
	user = current_user

@app.route('/infos/warning')
def infos():
	return render_template('warning_fake_site.html')

@app.route('/infos/how-is-this-site-made')
def howmade():
	return render_template('howimadethis.html')

@app.route('/getSharedFile/u/<filecode>')
@login_required
def getSharedFile(filecode):
	file = Files.query.filter_by(id=filecode).first()
	if file is not None:
		shared = file.shared
		filecode = file.id
		if shared == "True":
			name = file.filename
			filedir = file.filedir
			userupload = file.uploaduser
			return render_template("viewfile.html", filename=name, user=userupload, filecode=filecode, shared="True")
		else:
			return render_template("general-error.html", errorcode='FILE_NOT_SHARED_ERROR')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')

@app.route('/getSharedFile/a/<securitykeylink>/<filecode>')
def getSharedFileAll(securitykeylink, filecode):
	file = Files.query.filter_by(id=filecode).first()
	if file is not None:
		shared = file.shared
		securitykey = file.securitykey
		filecode = file.id
		if shared == "True":
			if securitykeylink == securitykey:
				name = file.filename
				filedir = file.filedir
				userupload = file.uploaduser
				return render_template("viewfile.html", filename=name, user=userupload, filecode=filecode, securitykey=securitykey, a="True", shared="True")
			else:
				return render_template("general-error.html", errorcode='SECURITY_KEY_INCORRECT')
		else:
			return render_template("general-error.html", errorcode='FILE_NOT_SHARED_ERROR')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')

@app.route('/getSharedFile/u/<filecode>/download')
@login_required
def getSharedFileDownload(filecode):
	file = Files.query.filter_by(id=filecode).first()
	if file is not None:
		shared = file.shared
		if shared == "True":
			name = file.filename
			filedir = file.filedir
			userupload = file.uploaduser
			print(filedir)
			return send_file(filedir, as_attachment=True)
		else:
			return render_template("general-error.html", errorcode='FILE_NOT_SHARED_ERROR')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')

@app.route('/getSharedFile/a/<securitykeylink>/<filecode>/download')
def getSharedFileAllDownload(securitykeylink, filecode):
	file = Files.query.filter_by(id=filecode).first()
	if file is not None:
		shared = file.shared
		securitykey = file.securitykey
		if shared == "True":
			if securitykeylink == securitykey:
				name = file.filename
				filedir = file.filedir
				userupload = file.uploaduser
				return send_file(filedir, as_attachment=True)
			else:
				return render_template("general-error.html", errorcode='SECURITY_KEY_INCORRECT')
		else:
			return render_template("general-error.html", errorcode='FILE_NOT_SHARED_ERROR')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')

#@app.route('/getOriginal/<filecode>')
#@login_required
#def getOriginal(filecode):
#	username = session.get("usernameglobale")
#	file = Files.query.filter_by(id=filecode).first()
#	if file is not None:
#		user = file.uploaduser
#		filedir = file.filedir
#		if username == user:
#			return send_file(filedir)
#		else:
#			return render_template("general-error.html", errorcode='INSUFFICIENT_PERMISSIONS')
#	else:
#		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')
		

@app.route('/viewFile/<filecode>', methods=['GET', 'POST'])
@login_required
def viewFile(filecode):
	username = session.get("usernameglobale")
	file = Files.query.filter_by(id=filecode).first()
	if filecode == '69':
		return redirect('https://git.leotecno.tk/rickroll.mp4')
	if file is not None:
		user = file.uploaduser
		filedir = file.filedir
		filename = file.filename
		filecode = file.id
		if username == user:
			return render_template('viewfile.html', filename=filename, filedir=filedir, user=user, filecode=filecode)
		else:
			return render_template('general-error.html', errorcode='INSUFFICIENT_PERMISSIONS')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')

@app.route('/viewFile/<filecode>/download', methods=['GET', 'POST'])
@login_required
def viewFileDownload(filecode):
	username = session.get("usernameglobale")
	file = Files.query.filter_by(id=filecode).first()
	if file is not None:
		user = file.uploaduser
		filedir = file.filedir
		filename = file.filename
		filecode = file.id
		if username == user:
			return send_file(filedir, as_attachment=True)
		else:
			return render_template('general-error.html', errorcode='INSUFFICIENT_PERMISSIONS')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')
		
@app.route('/viewFile/<filecode>/share', methods=['GET', 'POST'])
@login_required
def viewFileShare(filecode):
	username = session.get("usernameglobale")
	file = Files.query.filter_by(id=filecode).first()
	if file is not None:
		user = file.uploaduser
		filedir = file.filedir
		filename = file.filename
		filecode = file.id
		if username == user:
			if file.shared == "False":
				file.shared = "True"
				db.session.commit()
				flash("File condiviso!")
				return redirect('/')
			else:
				flash("File già condiviso!", category="error")
				return redirect('/')
		else:
			return render_template('general-error.html', errorcode='INSUFFICIENT_PERMISSIONS')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')

#@app.route('/test')
#def test():
#	return render_template('login_prox.html', title="e si ricomincia da 0...")







if __name__ == '__main__':
	app.run(host='192.168.1.101', port=80, debug=True)
	#file = Files.query.filter_by(id=72203501).first()
	#file.shared = "True"
	#db.session.commit()
	

