import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

# Setup Jinja2 template loader
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
jinja_env = Environment(loader=FileSystemLoader(templates_dir))


import httpx

async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send an HTML email via Resend HTTPS API (port 443) or fallback to SMTP."""
    # 1. Primary: Resend API over HTTPS (never blocked by Railway or cloud firewalls)
    if settings.RESEND_API_KEY:
        try:
            logger.info(f"Sending email to {to_email} via Resend HTTP API...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                resend_sender = settings.RESEND_FROM or "Sistema Trazabilidad <onboarding@resend.dev>"
                payload = {
                    "from": resend_sender,
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content
                }
                resp = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                if resp.status_code in (200, 201):
                    logger.info(f"Email successfully sent to {to_email} via Resend API")
                    return True
                else:
                    logger.warning(f"Resend API returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Error sending via Resend API: {e}. Falling back to SMTP...")

    # 2. Fallback: SMTP via aiosmtplib
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning(
            f"[SMTP MOCK] SMTP host/user not configured. Email to {to_email} skipped."
        )
        return True

    message = MIMEMultipart("alternative")
    message["From"] = settings.SMTP_FROM or settings.SMTP_USER
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(html_content, "html", "utf-8"))

    # Try configured port first, then try the other SSL/TLS port as fallback
    ports_to_try = []
    if settings.SMTP_PORT == 465 or not settings.SMTP_STARTTLS:
        ports_to_try = [(465, True, False), (587, False, True)]
    else:
        ports_to_try = [(587, False, True), (465, True, False)]

    last_error = None
    for port, use_tls, start_tls in ports_to_try:
        try:
            logger.info(f"Attempting SMTP connection to {settings.SMTP_HOST}:{port} (use_tls={use_tls}, start_tls={start_tls})...")
            smtp = aiosmtplib.SMTP(
                hostname=settings.SMTP_HOST,
                port=port,
                use_tls=use_tls,
                start_tls=start_tls,
                timeout=5,
            )
            await smtp.connect()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            await smtp.send_message(message)
            await smtp.quit()
            logger.info(f"Email successfully sent to {to_email} via port {port}")
            return True
        except Exception as e:
            last_error = e
            logger.warning(f"SMTP attempt to {to_email} via port {port} failed: {type(e).__name__}: {e}")

    logger.error(f"Failed to send email to {to_email} after all attempts: {last_error}")
    return False
