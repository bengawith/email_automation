from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
import pandas as pd
from io import StringIO
import time

from email_utils import validate_csv_columns, generate_email_content, send_graph_api_email

email_bp = Blueprint('email', __name__)

def token_required(func):
    """Decorator to ensure a valid token is present."""
    def wrapper(*args, **kwargs):
        token = session.get("token")
        expires_at = session.get("token_expires_at", 0)
        if not token or time.time() >= expires_at:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@email_bp.route("/email_form")
@token_required
def email_form():
    return render_template("email_form.html")

@email_bp.route("/preview_email", methods=["POST", "GET"])
@token_required
def preview_email():
    try:
        contacts_file = request.files.get('contacts_file')
        vendor_sales_file = request.files.get('vendor_sales_file')
        custom_message = request.form.get("custom_message", "")

        if not contacts_file or not contacts_file.filename.lower().endswith('.csv'):
            return "Contacts file must be a CSV", 400
        if not vendor_sales_file or not vendor_sales_file.filename.lower().endswith('.csv'):
            return "Vendor sales file must be a CSV", 400

        contacts_content = contacts_file.read().decode('utf-8')
        vendor_sales_content = vendor_sales_file.read().decode('utf-8')

        # Save contents to session for later use
        session['contacts_file'] = contacts_content
        session['vendor_sales_file'] = vendor_sales_content
        session['custom_message'] = custom_message

        contacts_df = pd.read_csv(StringIO(contacts_content))
        vendor_sales_df = pd.read_csv(StringIO(vendor_sales_content))

        validate_csv_columns(contacts_df, ['*ContactName', 'EmailAddress'], "Contacts CSV")
        validate_csv_columns(vendor_sales_df, ['Vendor Name', 'Gross Sales', 'Units Sold', 'Item Name'], "Vendor Sales CSV")

        contacts_df.columns = contacts_df.columns.str.strip()
        filtered_contacts = contacts_df[contacts_df['*ContactName'].str.contains(r'\*', na=False)].dropna(subset=['EmailAddress'])

        if filtered_contacts.empty:
            return "No valid contacts found in the contacts file", 400

        first_contact = filtered_contacts.iloc[0]
        vendor_name = first_contact['*ContactName'].strip()
        to_address = first_contact['EmailAddress'].strip()

        vendor_sales = vendor_sales_df[vendor_sales_df['Vendor Name'].str.strip() == vendor_name]

        email_content = generate_email_content(vendor_name, vendor_sales, custom_message)

        return render_template("preview_email.html", to_address=to_address, email_content=email_content)
    except Exception as e:
        current_app.logger.error("Error in preview_email: %s", e, exc_info=True)
        return f"An error occurred: {e}", 500

@email_bp.route("/send_email", methods=["POST"])
@token_required
def send_email():
    try:
        contacts_content = session.get('contacts_file')
        vendor_sales_content = session.get('vendor_sales_file')
        custom_message = session.get('custom_message')

        if not contacts_content or not vendor_sales_content:
            return "Missing contact or vendor sales files", 400

        contacts_df = pd.read_csv(StringIO(contacts_content))
        vendor_sales_df = pd.read_csv(StringIO(vendor_sales_content))

        contacts_df.columns = contacts_df.columns.str.strip()
        filtered_contacts = contacts_df[contacts_df['*ContactName'].str.contains(r'\*', na=False)].dropna(subset=['EmailAddress'])

        token = session.get("token")
        if not token:
            return redirect(url_for("auth.login"))

        for _, contact in filtered_contacts.iterrows():
            vendor_name = contact['*ContactName'].strip()
            to_address = contact['EmailAddress'].strip()

            vendor_sales = vendor_sales_df[vendor_sales_df['Vendor Name'].str.strip() == vendor_name]

            if vendor_sales.empty:
                current_app.logger.info("Empty sales CSV for vendor %s", vendor_name.replace('*', ''))
                continue

            if not to_address:
                current_app.logger.info("No email found for contact: %s", contact)
                continue

            email_content = generate_email_content(vendor_name, vendor_sales, custom_message)
            success = send_graph_api_email(to_address, "Your Monthly Sales Summary", email_content, token)
            if not success:
                current_app.logger.error("Failed to send email to %s", to_address)

        return render_template("success.html")
    except Exception as e:
        current_app.logger.error("Error in send_email: %s", e, exc_info=True)
        return f"An error occurred: {e}", 500
