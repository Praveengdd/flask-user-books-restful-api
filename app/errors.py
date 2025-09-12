from flask import jsonify

#Error Handlers for some common errors

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"Error": "Not Found"}), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"Error": "Something Went Wrong"}), 500