# AI Safety Guardian 🛡️

A beginner-friendly real-time safety monitoring system that detects falls and fire using computer vision and displays alerts on a Streamlit dashboard.

## Features
- **Fall Detection**: Uses YOLOv8-pose to detect human posture and flag potential falls.
- **Fire Detection**: Uses YOLOv8/Color-masking to identify fire or smoke.
- **Real-time Dashboard**: Built with Streamlit for live monitoring and alert history.

## Folder Structure
```
AI_Safety_Guardian/
├── dashboard.py       # Main Streamlit application
├── fall_detection.py  # Fall detection logic
├── fire_detection.py  # Fire detection logic
├── alert_system.py    # Alert logging and history
├── requirements.txt   # Project dependencies
└── README.md          # Documentation
```

## Installation

1. **Clone or Download** this project.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the dashboard using:
```bash
streamlit run dashboard.py
```

1. Open the URL provided by Streamlit (usually `http://localhost:8501`).
2. Click **Start Monitor** to begin webcam analysis.
3. Switch between detection modes using the sidebar.

## Dependencies
- Streamlit
- OpenCV
- Ultralytics (YOLOv8)
- NumPy
