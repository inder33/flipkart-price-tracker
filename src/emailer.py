import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from helpers import DYNAMIC_CHANGES_FILE

def send_summary_email(changed_count):

    csv_filename = DYNAMIC_CHANGES_FILE
    sender_email = os.getenv("sender_email")
    sender_password = os.getenv("EMAIL_PASSWORD") # 16-character App Password
    receiver_email = os.getenv("receiver_email")
    
    # --- Setup Multipart Message ---
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    
    # Dynamic Subject line featuring the dynamic count!
    msg['Subject'] = f"🔄 Scraper Update: Total {changed_count} product prices have been changed"
    
    # Clear, simplified text body
    body = f"""
    Hello,
    
    The Flipkart tracking scraper run has completed.
    
    I have sent you the updated tracking sheet attached below. It contains all the updated information detailing exactly which products changed, their current availability, and the updated price metrics.
    
    Total Products with Price Modifications: {changed_count}
    
    Please review the attached CSV file for full details.
    """
    msg.attach(MIMEText(body, 'plain'))
    
    # --- Attach CSV File ---
    if os.path.exists(csv_filename):
        try:
            with open(csv_filename, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(csv_filename)}",
            )
            msg.attach(part)
        except Exception as e:
            print(f"❌ Attachment failed: {e}")
            
    # --- Send Email ---
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"📨 Run Summary Email sent successfully for {changed_count} modifications!")
    except Exception as e:
        print(f"❌ Failed to send summary email: {e}")