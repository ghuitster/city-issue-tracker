from flask import Flask, jsonify
from flask.ext.sqlalchemy import SQLAlchemy


#TODO: Move Validation Error elsewhere?
class ValidationError(Exception):
	"""
	A simple Validation Error class for dealing with problems when models 
	Have invalid data that is set
	"""
	def __init__(self, msg):
		"""
		The init function for this error
		It takes in one argument which is the msg of what is wrong

		Keyword arguments:
		msg -- A string message that will be stored
		"""
		self.errorMsg = msg
	def __str__(self):
		return repr(self.errorMsg)

#TODO: Move genError elsewhere?
def genError(code, desc):
	"""
	A simple error code generate modeled after Open311's error codes

	Keyword arguments:
	code -- A http service code
	desc -- A string description of what will be passed back 
	"""

	# A jsonify Response that is generated
	jsonResp = jsonify({
		"code": code,
		"description": desc
	})

	jsonResp.status_code = code

	return jsonResp;


#Image upload settings
UPLOAD_FOLDER = 'data/img/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


import os
basedir = os.path.abspath(os.path.dirname(__file__))
#For local testing reasons
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')

db = SQLAlchemy(app)

#db.create_all()


from app import views



