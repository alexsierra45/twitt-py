from flask import Blueprint, request, jsonify

main = Blueprint('main', __name__)

@main.route('/users', methods=['POST'])
def crear_usuario():
    data = request.json
    user = {
        'name': data['name'],
        'email': data['email']
    }
    return jsonify(user), 201
