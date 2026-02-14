import resend
from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# Initialize Resend with API key
resend.api_key = settings.RESEND_API_KEY

# Email template for OTP
OTP_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your One-Time Password</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Poppins', Helvetica, Arial, sans-serif;
            background-color: #ffffff;
            -webkit-font-smoothing: antialiased;
        }}
        .wrapper {{
            width: 100%;
            background-color: #ffffff;
            padding: 40px 0;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            text-align: center;
        }}
        .logo-section {{
            padding-bottom: 50px;
        }}
        .logo {{
            width: 220px;
            height: auto;
        }}
        .content {{
            padding: 0 40px;
        }}
        h1 {{
            font-size: 24px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 15px;
        }}
        p {{
            font-size: 15px;
            color: #666666;
            line-height: 1.5;
            margin-bottom: 40px;
        }}
        .otp-wrapper {{
            display: inline-block;
            background-color: rgba(110, 69, 226, 0.1);
            border-radius: 12px;
            padding: 25px 45px;
            border: 1px solid rgba(110, 69, 226, 0.2);
        }}
        .otp-digits {{
            font-size: 42px;
            font-weight: 600;
            letter-spacing: 12px;
            color: #6e45e2;
            margin: 0;
            padding-left: 12px;
        }}
        .footer {{
            margin-top: 80px;
            font-size: 12px;
            color: #aaaaaa;
            border-top: 1px solid #f1f1f1;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="container">
            <div class="logo-section">
                <img src="https://github.com/DevyManish/kosix-backend/raw/master/assets/kosix-logo.png" alt="Kosix Logo" class="logo">
            </div>

            <div class="content">
                <h1>Verification Required</h1>
                <p>Please use the following One-Time Password (OTP) to complete your action. This code is valid for a limited time.</p>
                
                <div class="otp-wrapper">
                    <div class="otp-digits">{otp_code}</div>
                </div>

                <p style="margin-top: 40px; font-size: 13px; color: #999;">
                    If you did not request this code, please secure your account or contact support.
                </p>
            </div>

            <footer class="footer">
                &copy; {year} Kosix. All rights reserved.
            </footer>

        </div>
    </div>
</body>
</html>
"""


class EmailSender:
    """Utility class for sending emails using Resend."""

    @staticmethod
    def send_otp_email(
        to_email: str,
        otp_code: str,
        from_email: str = "Acme <onboarding@resend.dev>",
        subject: str = "Your Verification Code - Kosix"
    ) -> Optional[dict]:
        """
        Send OTP email to the specified email address.
        
        Args:
            to_email: Recipient email address
            otp_code: The 6-digit OTP code
            from_email: Sender email address (must be verified in Resend)
            subject: Email subject line
            
        Returns:
            Response from Resend API or None if failed
        """
        try:
            # Format the email template with OTP code and current year
            html_content = OTP_EMAIL_TEMPLATE.format(
                otp_code=otp_code,
                year=datetime.now().year
            )

            params: resend.Emails.SendParams = {
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }

            response = resend.Emails.send(params)
            logger.info(f"OTP email sent successfully to {to_email}")
            return response

        except Exception as e:
            logger.error(f"Failed to send OTP email to {to_email}: {str(e)}")
            return None

    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str = "noreply@kosix.com"
    ) -> Optional[dict]:
        """
        Send a custom email to the specified email address.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            from_email: Sender email address
            
        Returns:
            Response from Resend API or None if failed
        """
        try:
            params: resend.Emails.SendParams = {
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }

            response = resend.Emails.send(params)
            logger.info(f"Email sent successfully to {to_email}")
            return response

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return None


# Singleton instance for easy access
email_sender = EmailSender()
