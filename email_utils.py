import pandas as pd
import base64
from pathlib import Path
import logging
from config import Config

def validate_csv_columns(df, required_columns, file_label):
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"{file_label} is missing columns: {', '.join(missing)}")

def generate_email_content(vendor_name, sales_data, custom_message):
    """
    Generate an HTML-formatted email content string given sales data and a custom message.

    Args:
        vendor_name (str): The vendor name (with * prefix removed).
        sales_data (pd.DataFrame): The sales data for the vendor.
        custom_message (str): The custom message to include in the email.

    Returns:
        str: The generated HTML email content string.
    """
    try:
        sales_data = sales_data.copy()
        sales_data['Gross Sales'] = pd.to_numeric(
            sales_data['Gross Sales'].astype(str).str.replace('£', ''), errors='coerce'
        ).fillna(0)
        sales_data['Units Sold'] = pd.to_numeric(sales_data['Units Sold'], errors='coerce').fillna(0)
        total_sales = sales_data['Gross Sales'].sum()

        item_details = build_table(sales_data)

        signature_image_path = next(Path.cwd().rglob('static/images/MM_SIG.png'), None)
        if signature_image_path:
            with open(signature_image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            signature_image_html = f'<img src="data:image/png;base64,{encoded_image}" alt="MerseyMade Logo" class="img-fluid">'
        else:
            signature_image_html = ""

        signature = f"""
        <p>{Config().SIGNATURE_TEXT}<br>{signature_image_html}</p>
        """

        email_content = (
            f"Hello {vendor_name.strip()},<br><br>"
            + custom_message.replace('\n', '<br>') + "<br><br>"
            + item_details + "<br><br>"
            + f"Total Sales: £{total_sales:.2f}<br><br>"
            + signature
        )
        email_content = email_content.replace("<br><br><br>", "<br><br>")

        return f"""
        <html>
            <body>
                {email_content}
            </body>
        </html>
        """
    except Exception as e:
        logging.error("Error generating email content: %s", e)
        raise


def send_graph_api_email(to_address, subject, body, token):
    import requests
    endpoint = "https://graph.microsoft.com/v1.0/me/sendMail"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    email_data = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body
            },
            "toRecipients": [
                {"emailAddress": {"address": to_address}}
            ]
        }
    }
    response = requests.post(endpoint, headers=headers, json=email_data)
    print (response)
    if response.status_code == 202:
        logging.info("Email sent successfully to %s", to_address)
        return True
    else:
        logging.error("Failed to send email to %s - Status Code: %s, Response: %s",
                      to_address, response.status_code, response.text)
        return False


def build_table(sales_data: pd.DataFrame) -> str:
    """Build a HTML table from sales data for the email content."""
    try:
        item_details = "<table class='table table-bordered'>"
        item_details += "<thead><tr><th>Item Name</th>"
        if not sales_data['Item Variation'].isnull().all(axis=0):
            item_details += "<th>Item Variation</th>"
        item_details += "<th>Units Sold</th><th>Gross Sales</th></tr></thead>"
        item_details += "<tbody>"
        for _, row in sales_data.iterrows():
            item_details += "<tr>"
            item_details += f"<td>{row['Item Name']}</td>"
            if not sales_data['Item Variation'].isnull().all(axis=0):
                item_details += f"<td>{row['Item Variation']}</td>"
            item_details += f"<td>{int(row['Units Sold'])}</td>"
            item_details += f"<td>&pound;{row['Gross Sales']:.2f}</td>"
            item_details += "</tr>"
        item_details += "</tbody></table>"
        return item_details
    except Exception as e:
        logging.error("Error generating email content: %s", e, exc_info=True)
        raise
        