from flask import Flask, redirect, url_for, render_template
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
import logging

from config import Config
from auth import auth_bp, is_token_valid
from email_routes import email_bp
from errors import errors_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

    # Initialise server-side session and CSRF protection
    Session(app)
    CSRFProtect(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(errors_bp)

    @app.route("/")
    def index():
        if is_token_valid():
            return redirect(url_for("email.email_form"))
        return render_template("index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(app.config.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port, debug=True)
