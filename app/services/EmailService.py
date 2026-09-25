# The service is responsible only for sending emails

from email.message import EmailMessage

from aiosmtplib import SMTP

from app.core.config import settings


class EmailService:

    # Send a normal email
    @staticmethod
    async def send_email(
        recipient_email: str,
        subject: str,
        text_content: str,
        html_content: str,
    ) -> None:

        # Create the email message
        message = EmailMessage()

        # Set the sender
        message["From"] = settings.SMTP_FROM_EMAIL

        # Set the recipient
        message["To"] = recipient_email

        # Set the email subject
        message["Subject"] = subject

        # Add the plain text version
        message.set_content(text_content)

        # Add the HTML version
        message.add_alternative(
            html_content,
            subtype="html",
        )

        # Create SMTP connection
        smtp = SMTP(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            start_tls=True,
        )

        await smtp.connect()

        try:

            # Authenticate with SMTP server
            await smtp.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
            )

            await smtp.send_message(message)

        finally:
            await smtp.quit()

    # Send an email verification message
    @staticmethod
    async def send_verification_email(
        recipient_email: str,
        verification_token: str,
    ) -> None:

        # Create the verification URL
        verification_url = (
            f"{settings.APP_BASE_URL}"
            f"/auth/verify-email?token={verification_token}"
        )

        subject = "Verify your email address"

        text_content = f"""
Hello,

Please verify your email address by opening the link below:

{verification_url}

This verification link will expire in 30 minutes.

If you did not create this account, you can ignore this email.

Thank you.
"""

        # HTML email
        html_content = f"""
<html>
    <body>
        <h2>Verify your email address</h2>

        <p>Hello,</p>

        <p>
            Please click the button below to verify your email address.
        </p>

        <p>
            <a href="{verification_url}">
                Verify Email
            </a>
        </p>

        <p>
            This verification link will expire in 30 minutes.
        </p>

        <p>
            If you did not create this account,
            you can ignore this email.
        </p>

        <p>Thank you.</p>
    </body>
</html>
"""

        # Send the verification email
        await EmailService.send_email(
            recipient_email=recipient_email,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
        )