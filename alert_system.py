import smtplib
import time
import os
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==================================================
# PROBLEM 2: EMAIL CONFIGURATION
# ==================================================
# Replace these with your actual credentials for the demo
EMAIL_SENDER = "shemushemeer47@gmail.com"
EMAIL_PASSWORD = "vnwa wffj rexd ujov"
EMAIL_RECEIVER = "ms.shameer47@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Global list to store alert messages
alert_history = []

def send_email_alert(alert_type, confidence):
    """
    Sends an email alert using Gmail SMTP with validation and proper threading.
    """
    def _send():
        # Validation check
        if EMAIL_SENDER == "yourgmail@gmail.com" or EMAIL_PASSWORD == "16_char_gmail_app_password":
            print("❌ Email credentials missing: Please update alert_system.py with your Gmail credentials.")
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
                # SND_ASYNC plays in background, SND_FILENAME says it's a file
                winsound.PlaySound("alarm.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                print("🔊 Alarm triggered (wav file)!")
            else:
                # Fallback: Loop beeps several times to make it noticeable
                print("🔊 Alarm triggered (Beep fallback - wav missing)!")
                for _ in range(3):
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
