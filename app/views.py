import json
from flask import render_template, request, jsonify, Response
from app import app, db, ValidationError, genError
from fakeData import service_list, service_def, get_service_reqs, get_service_req, user_data
from models import Service, ServiceAttribute, Keyword, KeywordMapping, ServiceRequest, User, Note
from werkzeug.utils import secure_filename
from os import urandom
from passlib.hash import sha512_crypt
from datetime import datetime

JSON_ERR_MSG = "Invalid JSON or No JSON"

db.create_all()

############
# Helper functions
###########

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#############
# Main Page #
#############

#TODO: Make sure the html is being served up correctly
@app.route('/index')
@app.route('/')
def home():
	return render_template('index.html')

@app.route('/users.html')
def showUsers():
	return render_template('users.html')

################
# User Section #
################

#TODO: How to do this securely
@app.route('/users/sign_in', methods=['POST'])
def signIn():
	return "---"

#TODO: Implement
@app.route('/users/sign_out', methods=['POST'])
def signOut():
	return "---"

#TODO: Implement
@app.route('/users', methods=['POST'])
def createUser():
	'''
	Create a User
	'''
	
	if not request.json:
		return genError(400, JSON_ERR_MSG)

	requestJson = request.get_json()

	user = User()
	user.email = requestJson['email']
	user.firstName = requestJson['firstname']
	user.lastName = requestJson['lastname']
	user.phone = None
	user.role = 'admin' if requestJson['admin'] else 'user'

	# Generate a Cryptographically Secure Salt of length 16 bytes then generate the password
	# hash using the password and salt and hashing 10,000 times.
	password = requestJson['password']
	user.passwordSalt = urandom(16)
	user.passwordHash = sha512_crypt.encrypt(password, rounds = 10000, salt = user.passwordSalt)
	user.lastLogin = None
	user.joined = datetime.today()

	user.subscriptionList = []
	user = user.fromDict(requestJson)
	db.session.add(user)
	db.session.commit()

	return user.toJSON()

#TODO: Implement
@app.route('/users/<int:user_id>', methods=['GET'])
def getUser(user_id):
	'''
	Retrieve a User's information
	'''
	user = User.query.get(user_id)

	if user == None:
		return genError(404, "User ID was not found");

	return user.toCitJSON();



#TODO: Implement
@app.route('/users/<int:user_id>', methods=['POST'])
def updateUser(user_id):

	if not request.json:
		return genError(400, JSON_ERR_MSG)

	requestJson = request.get_json()

	user = User.query.get(user_id)

	user.email = requestJson['email']
	user.firstName = requestJson['name']
	user.lastName = requestJson['name']
	user.role = 'admin' if requestJson['admin'] else 'user'
	if requestJson['password']:
		password = requestJson['password']
		user.passwordSalt = urandom(16)
		user.passwordHash = sha512_crypt.encrypt(password, rounds = 10000, salt = user.passwordSalt)
	user = user.fromDict(requestJson)
	db.session.add(user)
	db.session.commit()

	return user.toJSON()

#TODO: Implement
@app.route('/users/signed_in_user')
def getOwnAccount():
	return "---"

#TODO: Implement
@app.route('/users', methods=['GET'])
def getAllUsers():
	'''
	Return all users. Pagination is not implemented yet, so offset will always be 0, and total_results and total_returned will always be the same.
	'''
	allUsers = User.query.all()
	userArray = []

	for user in allUsers:
		userArray.append(user.toCITDict())

	return jsonify
	(
		{
			"total_results": len(allUsers),
			"total_returned": len(allusers),
			"offset": 0,
			"users": userArray
		}
	)


###################
# Service Section #
###################

#Create a new service
@app.route('/services', methods=['POST'])
def newService():

	if not request.json:
		return genError(400, JSON_ERR_MSG)

	s = Service()
	s.fromDict(request.json)

	db.session.add(s)
	db.session.commit()

	jsonResp = s.toJSON()
	jsonResp.status_code = 201

	return jsonResp

#Get a list of all services
@app.route('/services', methods=['GET'])
def getServices():
	l = Service.query.all()

	return Service.composeFormatList("json", l)

#Get a specific service
@app.route('/services/<int:serviceId>', methods=['GET'])
def getService(serviceId):
	s = Service.query.get(serviceId)

	if s == None:
		return genError(404, "Service ID was not found");

	return s.toCitJSON();

#Updates a service
@app.route('/services/<int:serviceId>', methods=['POST'])
def postService(serviceId):

	#TODO: Check if json will error out
	if not request.json:
		return genError(400, JSON_ERR_MSG)

	s = Service.query.get(serviceId)

	if s == None:
		return genError(404, "Service ID was not found");

	try:
		s.fromDict(request.json)
	except ValidationError as e:
		return genError(400, e.errorMsg)

	db.session.commit()

	return s.toJSON()

@app.route('/services/<int:serviceId>', methods=['DELETE'])
def deleteService(serviceId):

	s = Service.query.get(serviceId)

	db.session.delete(s)
	db.session.commit()

	#TODO: Some other way of marking success
	return "---"



#TODO: Implement
@app.route('/services/<int:serviceId>/attr', methods=['GET'])
def getServiceAttr(serviceId):
	sa1 = ServiceAttribute()


	sa2 = ServiceAttribute()


	sa3 = ServiceAttribute()

	return "---"



##################
# Issues Section #
##################

#TODO: Test and deal with user authorization
@app.route('/issues/<int:issue_id>', methods=['GET'])
def getIssue(issue_id):
	"""
	Return the issue with id = issue_id
	"""

	serviceRequest = ServiceRequest.query.get(issue_id)

	if serviceRequest == None:
		return genError(404, "Issue ID was not found");

	return serviceRequest.toCitJSON()

#TODO: Test and deal with user authorization
@app.route('/issues', methods=['POST'])
def createIssue():
	"""
	Create an issue
	"""

	requestJson = request.get_json()

	if not requestJson:
		return genError(400, JSON_ERR_MSG)

	serviceRequest = ServiceRequest()
	serviceRequest.lat = requestJson["location"]["lat"]
	serviceRequest.longitude = requestJson["location"]["long"]
	serviceRequest.address = requestJson["location"]["address"]
	#serviceRequest.requestedDatetime = strftime("%Y-%m-%d %H:%M:%S", localtime())
	#serviceRequest.updatedDatetime = strftime("%Y-%m-%d %H:%M:%S", localtime())

	try:
		serviceRequest.fromCitDict(requestJson);
	except ValidationError as e:
		return genError(400, e.errorMsg)

	db.session.add(serviceRequest)
	db.session.commit()

	return serviceRequest.toCitJSON()

#TODO: Test and deal with user authorization
@app.route('/issues/<int:issue_id>', methods=['POST'])
def updateIssue(issue_id):
	"""
	Update the given issue
	"""

	requestJson = request.get_json()

	if not requestJson:
		return genError(400, JSON_ERR_MSG)

	serviceRequest = ServiceRequest.query.get(issue_id)
	serviceRequest.lat = requestJson["location"]["lat"]
	serviceRequest.longitude = requestJson["location"]["long"]
	serviceRequest.address = requestJson["location"]["address"]
	#serviceRequest.updatedDatetime = localtime().strftime("%Y-%m-%d %H:%M:%S")

	try:
		serviceRequest.fromCitDict(requestJson);
	except ValidationError as e:
		return genError(400, e.errorMsg)

	db.session.commit()

	return serviceRequest.toCitDict()

#TODO: Test and deal with user authorization
@app.route('/issues', methods=['GET'])
def viewAllIssues():
	"""
	Return all the issues
	"""

	requestJson = request.get_json()

	#If there is no json that is ok since we have defaults
	if not requestJson:
		requestJson = {}


	#TODO: Have defaults
	orderBy = requestJson.get("orderBy", "created_at")
	offset = int(requestJson.get("offset", 0))
	max = int(requestJson.get("max", 50))
	query = requestJson.get("query", "")
	reversed = bool(requestJson.get("reversed", False))
	includeClosed = bool(requestJson.get("includeClosed", False))

	if not query == "":
		query = ServiceRequest.query.filter(ServiceRequest.title.contains(query) or ServiceRequest.description.contains(query)).filter(True if includeClosed else ServiceRequest.status == "open")
	else:
		query = ServiceRequest.query.filter(True if includeClosed else ServiceRequest.status == "open")

	if orderBy == "created_at":
		allIssues = query.order_by(ServiceRequest.requestedDatetime).all()
	elif orderBy == "priority":
		allIssues = query.order_by(ServiceRequest.priority).all()
	elif orderBy == "open":
		allIssues = query.order_by(ServiceRequest.status).all()

	requestArray = []

	for i in range(len(allIssues)):
		if len(requestArray) < max:
			try:
				if reversed:
					serviceRequest = allIssues[-(i + offset)]
				else:
					serviceRequest = allIssues[i + offset]

				notes = serviceRequest.statusNotes
				notesArray = []

				for i in range(len(notes)):
					notesArray.append
					(
						{
							"created_at" : notes[i].createdAt,
							"note" : notes[i].note
						}
					)

				s = serviceRequest.toCitDict()
				s["notes"] = notesArray

				requestArray.append(s)
			except:
				break
		else:
			break

	return jsonify({
		"total_results": len(allIssues),
		"total_returned": len(requestArray),
		"offset": offset,
		"issues": requestArray
	})

#TODO: Implement
@app.route('/issues/images', methods=['POST'])
def uploadImage():
	"""
	Upload an image
	"""
	#This code is from flask website mostly
	file = request.files['file']
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		#TODO: Have someway of using a hash for the file name
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		return redirect(url_for('uploaded_file', filename=filename))

	return "---"

#TODO: Implement
@app.route('/issues/images/<int:photo_id>', methods=['GET'])
def viewImage(photo_id):
	"""
	Return the photo with id = photo_id
	"""
	return "---"


######################
# Open311 API Routes #
######################

#TODO: Implement
@app.route('/open311/api/services.<form>', methods=['GET'])
def json_view_services(form):
	l = Service.query.all()

	return Service.composeFormatList(form, l)

@app.route('/open311/api/services/<int:serviceCode>.<form>')
def apiViewService(serviceCode, form):
		

	return "---"

#TODO: Implement
@app.route('/open311/api/issue/<int:issue_id>.<form>', methods = ['GET'])
def json_view_issue(issue_id, format):
	return format
#	return jsonify(get_service_req)

#TODO: Implement
@app.route('/open311/api/issues', methods = ['GET'])
def json_view_issues():
	return jsonify(get_service_reqs)

##################
# Error Handlers #
##################

#TODO: Implement
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

#TODO: Implement
@app.errorhandler(405)
def page_not_found(e):
	return render_template('405.html'), 405
