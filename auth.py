from flask import Blueprint, redirect, url_for, request, session, current_app
import msal
import time

auth_bp = Blueprint('auth', __name__)

def init_msal(app):
    client_id = app.config['CLIENT_ID']
    client_secret = app.config['CLIENT_SECRET']
    tenant_id = app.config['TENANT_ID']
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    msal_app = msal.ConfidentialClientApplication(
        client_id=client_id,
        authority=authority,
        client_credential=client_secret
    )
    return msal_app

def is_token_valid():
    token = session.get("token")
    expires_at = session.get("token_expires_at", 0)
    if token and time.time() < expires_at:
        return True
    return False

@auth_bp.route("/login")
def login():
    msal_app = init_msal(current_app)
    redirect_uri = current_app.config['REDIRECT_URI']
    scope = current_app.config['MSAL_SCOPE']
    auth_url = msal_app.get_authorization_request_url(
        scopes=scope,
        redirect_uri=redirect_uri
    )
    current_app.logger.info("Redirecting to OAuth URL: %s", auth_url)
    return redirect(auth_url)

@auth_bp.route("/authorized")
def authorized():
    code = request.args.get("code")
    if not code:
        return "No authorization code provided", 400

    msal_app = init_msal(current_app)
    redirect_uri = current_app.config['REDIRECT_URI']
    scope = current_app.config['MSAL_SCOPE']
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=scope,
        redirect_uri=redirect_uri
    )

    if "access_token" in result:
        session["token"] = result["access_token"]
        session["token_expires_at"] = time.time() + result.get("expires_in", 3600)
        current_app.logger.info("User logged in successfully.")
        return redirect(url_for("email.email_form"))
    else:
        current_app.logger.error("Login failed: %s", result.get("error_description"))
        return "Login failed. Please try again.", 400

@auth_bp.route("/logout")
def logout():
    session.clear()
    current_app.logger.info("User logged out")
    return redirect(url_for("index"))
