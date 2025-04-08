from flask import Blueprint, render_template

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("error.html", error="Page not found", traceback=""), 404

@errors_bp.app_errorhandler(500)
def internal_error(error):
    return render_template("error.html", error="Internal server error", traceback=""), 500
