from . import api
from app.exceptions import ValidationError
from flask import jsonify
def forbidden(message):
	response=jsonify({'error':'forbdden','message':message})
	response.status_code=403
	return response
@api.errorhandler(ValidationError)
def validation_error(e):
	return bad_request(e.args[0])
