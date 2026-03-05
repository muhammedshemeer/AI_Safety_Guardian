import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import time
import os
from alert_system import play_alarm, send_email_alert, log_alert, get_alert_history, EMAIL_SENDER, EMAIL_PASSWORD
from fall_detection import detect_fall
from fire_detection import detect_fire

# Page Configuration
st.set_page_config(page_title="AI Safety Guardian", page_icon="🛡️", layout="wide")

# Initialize Session State
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'fall_start_time' not in st.session_state:
    st.session_state.fall_start_time = None
if 'alert_triggered' not in st.session_state:
    st.session_state.alert_triggered = False

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ AI Safety Guardian Dashboard")
st.write("Real-time Fall and Fire Detection System with Advanced Escalation")

# Load Models
@st.cache_resource
def load_models():
    pose_model = YOLO('yolov8n-pose.pt')
    detect_model = YOLO('yolov8n.pt') 
    return pose_model, detect_model

pose_model, detect_model = load_models()

# Sidebar - Settings & History
st.sidebar.header("Settings")
detection_mode = st.sidebar.selectbox("Choose Detection Mode", ["All", "Fall Detection", "Fire Detection"])
show_confidence = st.sidebar.checkbox("Show Confidence Scores", value=True)

st.sidebar.divider()
st.sidebar.header("⚙️ System Configuration")

# Check Alarm File
if not os.path.exists("alarm.wav"):
    st.sidebar.warning("⚠️ alarm.wav not found! System will use internal Beep.")
else:
    st.sidebar.success("✅ alarm.wav found.")

# Check Email Config
if EMAIL_SENDER == "yourgmail@gmail.com" or EMAIL_PASSWORD == "16_char_gmail_app_password":
    st.sidebar.error("❌ Email not configured! Setup App Password in alert_system.py.")
else:
    st.sidebar.success("✅ Email configured.")

st.sidebar.divider()
st.sidebar.header("🚨 Alert History")
alert_history_placeholder = st.sidebar.empty()

# Action Buttons
if st.sidebar.button("Start Monitor"):
    st.session_state.monitoring_active = True
if st.sidebar.button("Stop Monitor"):
    st.session_state.monitoring_active = False
    st.session_state.fall_start_time = None
    st.session_state.alert_triggered = False

# Main Dashboard Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Feed")
    frame_placeholder = st.empty()

with col2:
    st.subheader("System Status")
    status_placeholder = st.empty()
    
    col_fall, col_fire = st.columns(2)
    with col_fall:
        fall_metric = st.empty()
    with col_fire:
        fire_metric = st.empty()
    
    st.divider()
    st.subheader("Active Alerts")
    alert_placeholder = st.empty()

# Monitoring Loop
if st.session_state.monitoring_active:
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened() and st.session_state.monitoring_active:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to access webcam.")
            break

        # Process frame based on selected mode
        fall_res = {"fall_detected": False, "confidence": 0.0}
        fire_res = {"fire_detected": False, "confidence": 0.0}

        if detection_mode in ["All", "Fall Detection"]:
            fall_res = detect_fall(frame, pose_model)
        
        if detection_mode in ["All", "Fire Detection"]:
            fire_res = detect_fire(frame, detect_model)

        # --------------------------------------------------
        # FEATURE 1: 3-SECOND FALL CONFIRMATION LOGIC
        # --------------------------------------------------
        if fall_res["fall_detected"]:
            # If this is the start of a new fall detection, record the time
            if st.session_state.fall_start_time is None:
                st.session_state.fall_start_time = time.time()
            
            # Calculate how long the fall has been persisting
            elapsed_time = time.time() - st.session_state.fall_start_time
            
            # If fall persists for >= 3 seconds AND we haven't triggered the alert yet
            if elapsed_time >= 3.0 and not st.session_state.alert_triggered:
                # Trigger Escalation (Alarm + Email)
                alert_msg = f"{time.strftime('%H:%M:%S')} - CONFIRMED FALL ({fall_res['confidence']:.2f})"
                log_alert(alert_msg)
                
                # These functions now work reliably and non-blocking
                play_alarm()
                send_email_alert("Fall Detected", fall_res['confidence'])
                
                # Mark as triggered so it only plays once PER fall event
                st.session_state.alert_triggered = True
                
        else:
            # IMPORTANT: When fall stops, we reset everything.
            # This allows the alarm to trigger again if a NEW fall happens later.
            st.session_state.fall_start_time = None
            st.session_state.alert_triggered = False 

        # Update Live Feed
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB")

        # Update Metrics
        if show_confidence:
            fall_metric.metric("Fall Conf", f"{fall_res['confidence']:.2f}")
            fire_metric.metric("Fire Conf", f"{fire_res['confidence']:.2f}")

        # Update Status & Notifications
        if st.session_state.alert_triggered:
            status_placeholder.error("🚨 CONFIRMED FALL")
            alert_placeholder.error("EMERGENCY: Fall detected and confirmed!")
        
        elif fall_res["fall_detected"]:
            status_placeholder.warning("⚠️ Potential Fall...")
            wait_time = 3.0 - (time.time() - st.session_state.fall_start_time)
            alert_placeholder.warning(f"Confirming fall in {max(0.0, wait_time):.1f}s...")
        
        elif fire_res["fire_detected"]:
            status_placeholder.error("🔥 FIRE DETECTED")
            alert_msg = f"{time.strftime('%H:%M:%S')} - FIRE DETECTED ({fire_res['confidence']:.2f})"
            log_alert(alert_msg)
            alert_placeholder.warning("Fire/Smoke risk detected!")
        
        else:
            status_placeholder.success("✅ System Monitoring...")
            alert_placeholder.info("No active threats detected.")

        # Update History in Sidebar
        history = get_alert_history()
        with alert_history_placeholder.container():
            for h in history[:10]:
                st.text(h)

    cap.release()
else:
    status_placeholder.info("System Offline. Click 'Start Monitor' to begin.")
