from flask import Flask, Blueprint, render_template, request, flash, redirect, session, url_for, send_file, send_from_directory, abort
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
import secrets
import threading

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

#Definition of processes
def databaseCreation(app):
	if not path.exists('/instance/databaseUsers.db'):
		with app.app_context():
			db.create_all()
			#db.drop_all()
			#print('Database Created!')

#def LoadingPage():
#	while uploaded == 0:
#		return "Caricamento del file, perfavore attendere..."
#	if uploaded == 1:
#		return redirect('/UserDashboard')

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
	#id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(100), primary_key=True)
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

@app.route('/static/<path:path>')
def serve_static_file(path):
	protected_directories = ['fonts', 'images', 'scripts', 'users']

	if any(dir in path for dir in protected_directories):
		abort(403)

	return send_from_directory('static', path)



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

@app.route('/account/login', methods=['GET', 'POST'])
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
				return redirect(url_for('UserDashboard'))
				 
			else:
				flash('Password non corretta.', category='error')
		else:
			flash('Utente inesistente o email errata.', category='error')
	#else:
	#	flash('Il server non è in grado di gestire la richiesta in questo momento.')

	return render_template('login_prox.html', user=current_user, navbar='withhome', title="FilEZ | Login")



@app.route('/account/register', methods=['GET', 'POST'])
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
			return redirect(url_for('UserDashboard'))

		

	return render_template('register.html')

@app.route('/coming-soon')
def comingsoon():
	return "Coming soon! © Filez 2023 LeoTecno"

@app.route('/trolling-time')
def trollingtime():
	print("+ un rickrollato")
	time.sleep(3)
	return redirect('https://git.leotecno.tk')

@app.route('/account/logout')
@login_required
def logout():
	logout_user()
	flash("Logout effettuato con successo!")
	return redirect('/account/login')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
	uploaded = 0
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

				#string_length = 8
				#id = ''.join([random.choice('0123456789') for n in range(string_length)])
				#print (id)
				id = ''.join(random.choice(string.ascii_letters) for i in range(25))
				alfabeto = string.ascii_letters + string.digits
				securitykey = ''.join(secrets.choice(alfabeto) for i in range(30))
				filedirdb = user_folder + '/' + file.filename
				fileExists = os.path.exists(filedirdb)

				if fileExists == True:
					flash ("Hai già caricato un file con questo nome!", category="error")
					return redirect('/UserDashboard')
			
				else:	
					#shared = request.form.getlist('shared')
					#print (shared)
					thingstoadd = Files(filecode=id, filename=file.filename, uploaduser=usernameglobale, filedir=filedirdb, shared='False', shareduser="None", securitykey=securitykey)
					db.session.add(thingstoadd)
					db.session.commit()
					file.save(os.path.join(app.config["UPLOADED_FILE_FOLDER_FOR_USER"], file.filename))
					flash("File caricato!")
					print(file.filename)
					
			#return render_template(url_for('yourfile.html', filename=file.filename))
		
		else:
			flash("C'è stato un errore, riprova.", category="error")



	return redirect('/UserDashboard')

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
	#app.config['FILES'] = "//RASPBERRYPI/Leo/Workstation/FilezAlpha/static/users/uploaded_files/"
	username = session.get("usernameglobale")
	#path = '//RASPBERRYPI/Leo/Workstation/FilezAlpha/static/users/leo/uploaded/'
	#files = os.listdir(path)
	files = Files.query.filter_by(uploaduser=username).all()
	#for file in files:
	#	if os.path.isfile(os.path.join(path, file)):
	#		print (file)
	return render_template('dashboard.html', name=username, files=files)

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

@app.route('/sharedFile/<filecode>/u')
@login_required
def getSharedFile(filecode):
	file = Files.query.filter_by(filecode=filecode).first()
	if file is not None:
		shared = file.shared
		filecode = file.filecode
		if shared == "True":
			name = file.filename
			filedir = file.filedir
			userupload = file.uploaduser
			filename_no_ext, fileext = os.path.splitext(name)
			return render_template("viewfile.html", filename=name, user=userupload, filecode=filecode, sharemode='U', shared="True", fileext=fileext)
		else:
			return render_template("general-error.html", errorcode='FILE_NOT_SHARED_ERROR')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')

@app.route('/sharedFile/<filecode>/<securitykeylink>/a')
def getSharedFileAll(securitykeylink, filecode):
	file = Files.query.filter_by(filecode=filecode).first()
	if file is not None:
		shared = file.shared
		securitykey = file.securitykey
		filecode = file.filecode
		if shared == "True":
			if securitykeylink == securitykey:
				name = file.filename
				filedir = file.filedir
				userupload = file.uploaduser
				filename_no_ext, fileext = os.path.splitext(name)
				return render_template("viewfile.html", filename=name, user=userupload, filecode=filecode, securitykey=securitykey, sharemode='A', shared="True", fileext=fileext)
			else:
				return render_template("general-error.html", errorcode='SECURITY_KEY_INCORRECT')
		else:
			return render_template("general-error.html", errorcode='FILE_NOT_SHARED_ERROR')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')

@app.route('/sharedFile/<filecode>/u/download')
@login_required
def getSharedFileDownload(filecode):
	file = Files.query.filter_by(filecode=filecode).first()
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

@app.route('/sharedFile/<filecode>/<securitykeylink>/a/download')
def getSharedFileAllDownload(securitykeylink, filecode):
	file = Files.query.filter_by(filecode=filecode).first()
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
		

@app.route('/file/<filecode>/view', methods=['GET', 'POST'])
@login_required
def viewFile(filecode):
	username = session.get("usernameglobale")
	file = Files.query.filter_by(filecode=filecode).first()
	if filecode == '69':
		return redirect('https://git.leotecno.tk/rickroll.mp4')
	if file is not None:
		user = file.uploaduser
		filedir = file.filedir
		filename = file.filename
		filecode = file.filecode
		sharedbyme = file.shared
		if username == user:
			filename_no_ext, fileext = os.path.splitext(filename)
			return render_template('viewfile.html', filename=filename, filedir=filedir, user=user, filecode=filecode, fileext=fileext, sharedbyme=sharedbyme)
		else:
			return render_template('general-error.html', errorcode='INSUFFICIENT_PERMISSIONS')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')



@app.route('/file/<filecode>/download', methods=['GET', 'POST'])
@login_required
def viewFileDownload(filecode):
	username = session.get("usernameglobale")
	file = Files.query.filter_by(filecode=filecode).first()
	if file is not None:
		user = file.uploaduser
		filedir = file.filedir
		filename = file.filename
		filecode = file.filecode
		if username == user:
			return send_file(filedir, as_attachment=True)
		else:
			return render_template('general-error.html', errorcode='INSUFFICIENT_PERMISSIONS')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')
		
@app.route('/file/<filecode>/share', methods=['GET', 'POST'])
@login_required
def viewFileShare(filecode):
	sharemode = request.form.get('share')
	username = session.get("usernameglobale")
	file = Files.query.filter_by(filecode=filecode).first()
	if file is not None:
		user = file.uploaduser
		filedir = file.filedir
		filename = file.filename
		filecode = file.filecode
		if username == user:
			if file.shared == "False":
				file.shared = "True"
				db.session.commit()
				if sharemode == 'A':
					filecode = file.filecode
					securitykey = file.securitykey
					link = 'http://192.168.1.101/sharedFile/' + filecode + '/' + securitykey + '/a'
					print (link)
				if sharemode == 'U':
					link = 'http://192.168.1.101/sharedFile/' + filecode + '/u'
					print (link)
				flash("File condiviso!")
				return redirect('/UserDashboard')
			else:
				flash("File già condiviso!", category="error")
				return redirect('/UserDashboard')
		else:
			return render_template('general-error.html', errorcode='INSUFFICIENT_PERMISSIONS')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')
	
@app.route('/file/<filecode>/delete', methods=['GET', 'POST'])
@login_required
def viewFileDel(filecode):
	username = session.get("usernameglobale")
	file = Files.query.filter_by(filecode=filecode).first()
	if file is not None:
		user = file.uploaduser
		filedir = file.filedir
		filename = file.filename
		filecode = file.filecode
		if username == user:
			file_to_delete = '//RASPBERRYPI/Leo/Workstation/FilezAlpha/static/users/' + username + '/uploaded/' + filename
			os.remove(file_to_delete)
			db.session.delete(file)
			db.session.commit()
			flash('File cancellato con successo!', category='success')
			return redirect('/UserDashboard')
		else:
			return render_template('general-error.html', errorcode='INSUFFICIENT_PERMISSIONS')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')
	
@app.route('/file/<filecode>/removeshare', methods=['GET', 'POST'])
@login_required
def viewFileRemoveShare(filecode):
	username = session.get("usernameglobale")
	file = Files.query.filter_by(filecode=filecode).first()
	if file is not None:
		user = file.uploaduser
		filedir = file.filedir
		filename = file.filename
		filecode = file.filecode
		if username == user:
			if file.shared == "True":
				file.shared = "False"
				db.session.commit()
				flash("File non più condiviso!", category='success')
				return redirect('/UserDashboard')
			else:
				flash("File non ancora condiviso!", category="error")
				return redirect('/UserDashboard')
		else:
			return render_template('general-error.html', errorcode='INSUFFICIENT_PERMISSIONS')
	else:
		return render_template("general-error.html", errorcode='FILE_NOT_FOUND_ERROR')	

@app.route('/UserDashboard/search')
def search():
	username = session.get("usernameglobale")
	query = request.args.get('query', '')
	files = Files.query.filter(Files.uploaduser == username, Files.filename.ilike(f'%{query}%')).all()
	return render_template('dashboard.html', files=files, query=query, name=username)


@app.route('/test')
def test():
	flash('Questo è un test')
	return render_template('home.html')





if __name__ == '__main__':
	app.run(host='192.168.1.101', port=80, debug=True)
	#file = Files.query.filter_by(id=72203501).first()
	#file.shared = "True"
	#db.session.commit()
	

