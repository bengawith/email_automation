# Sales Summary Email Automation

This project is a modular Flask application that automates sending monthly sales summary emails based on uploaded CSV files. It uses Microsoft Graph API with MSAL for authentication to send the emails from the authenticated mailbox, and processes CSV data to generate email content. The email signature and other configurations are managed via environment variables.

## Features

- **CSV Upload & Processing:**  
  Validate and process contacts and vendor sales CSV files with required columns.

- **Email Preview & Sending:**  
  Generate a preview of the email content and send emails using the Microsoft Graph API.

- **MSAL Authentication:**  
  Authenticate using OAuth2 to securely acquire access tokens for sending emails.

- **Modular Code Structure:**  
  Clean separation of configuration, authentication, email handling, and error handling.

- **Environment-Based Configuration:**  
  All sensitive and environment-specific settings are loaded from a `.env` file.

## Directory Structure

```
root/
├── config.py            # Application configuration and environment variables.
├── auth.py              # Routes and functions for OAuth/MSAL authentication.
├── email_routes.py      # Routes for the email form, preview, and sending.
├── email_utils.py       # Utility functions for CSV validation, email content generation, and sending.
├── errors.py            # Custom error handlers.
├── main.py              # Application factory and entry point.
├── .env                 # Environment variables file.
├── requirements.txt     # Python dependencies.
├── templates/           # HTML templates.
│   ├── base.html
│   ├── email_form.html
│   ├── error.html
│   ├── index.html
│   ├── preview_email.html
│   └── success.html
└── static/
    └── images/
        ├── merseymade_cover.jfif
        └── MM_SIG.png
```

## Installation

### Prerequisites

- Python 3.7 or later
- pip

### Steps

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd project_root
   ```

2. **Create & Activate a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows, use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Create or update your `.env` file with the following variables:
   ```dotenv
   SECRET_KEY=your-secret-key
   CLIENT_ID=your-ms-client-id
   CLIENT_SECRET=your-ms-client-secret
   TENANT_ID=your-ms-tenant-id
   REDIRECT_URI=https://your-deployment-domain.com/authorized
   SIGNATURE_TEXT=signature-text-for-email
   ```
   Adjust the values as needed for your environment.

## Running the Application Locally

1. **Set the Environment Variables:**  
   Make sure your `.env` file is located at the project root.

2. **Start the Flask Application:**
   ```bash
   python main.py
   ```
3. **Access the Application:**  
   Open your browser at [http://127.0.0.1:5000/](http://127.0.0.1:5000/) to use the app.

### Example for Deployment on Render:

1. **Create a New Web Service:**  
   Choose Render's Python web service option.

2. **Configure Build & Start Commands:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:app`

3. **Add Environment Variables:**  
   Import the contents of your `.env` file into Render’s dashboard.

## License

This project is intended for personal and internal use. Modifications and improvements are welcome.

## Contact

For any questions or issues, feel free to [contact me](mailto:ben@gawith.com) for more information.