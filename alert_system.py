import smtplib
import time
import os
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==================================================
# PROBLEM 2: EMAIL CONFIGURATION
# ==================================================
# Credentials loaded from .env securely
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

# Global list to store alert messages
alert_history = []

def send_email_alert(alert_type, confidence):
    """
    Sends an email alert using Gmail SMTP with validation and proper threading.
    """
    def _send():
        # Validation check
        if not EMAIL_SENDER or not EMAIL_PASSWORD or EMAIL_SENDER == "yourgmail@gmail.com":
            print("❌ Email credentials missing: Please update your .env file with your Gmail credentials.")
            return

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_RECEIVER
            msg['Subject'] = "🚨 AI Safety Guardian Alert"

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            body = f"""
            Fall detected in monitored area.
            
            Details:
            - Timestamp: {timestamp}
            - Alert Type: {alert_type}
            - Detection Confidence: {confidence:.2f}
            
            Please check the dashboard immediately.
            """
            msg.attach(MIMEText(body, 'plain'))

            # Setup SMTP server
            print(f"Connecting to {SMTP_SERVER}...")
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f"✅ Email alert successfully sent to {EMAIL_RECEIVER}")
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")

    # Run in background thread to prevent Streamlit UI from lag/freezing
    thread = threading.Thread(target=_send)
    thread.start()

def play_alarm():
    """
    Plays the emergency alarm sound.
    Uses winsound.SND_ASYNC or a threaded beep loop to prevent blocking.
    """
    def _play():
        try:
            import winsound
            if os.path.exists("alarm.wav"):
                print("🔊 Alarm triggered (wav file)!")
                # Play synchronously multiple times in this background thread
                for _ in range(3):
                    winsound.PlaySound("alarm.wav", winsound.SND_FILENAME)
            else:
                # Fallback: Loop beeps to last ~3.6 seconds
                print("🔊 Alarm triggered (Beep fallback - wav missing)!")
                for _ in range(6):
                    winsound.Beep(1000, 500)  # 1kHz for 0.5s
                    time.sleep(0.1)
        except Exception as e:
            print(f"Error playing alarm: {e}")

    # Run in thread so the Beep loop doesn't freeze the camera
    threading.Thread(target=_play, daemon=True).start()

def log_alert(message):
    """
    Stores an alert message in the history if it's not a duplicate within the same detection cycle.
    """
    if not alert_history or alert_history[0] != message:
        alert_history.insert(0, message)

def get_alert_history():
    """
    Returns the list of stored alerts.
    """
    return alert_history
