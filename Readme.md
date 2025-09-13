# Ai Fitness Trainer

A real-time pushup counter application that uses computer vision to track pushups, monitor form, and provide feedback on camera placement and lighting. Built with Python, MediaPipe, OpenCV, and Streamlit, this app turns your webcam into a virtual fitness coach!

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features
- **Real-Time Pushup Tracking**: Counts pushups using pose estimation, supporting both front and side views.
- **Form Feedback**: Detects if your body is aligned properly during pushups and provides real-time feedback.
- **Camera Placement Guidance**: Alerts you if the camera is too close, too far, or if lighting is insufficient.
- **Interactive Web Interface**: Built with Streamlit for a user-friendly experience, including a reset button for the counter.
- **Visual Overlays**: Displays landmarks, angles, and status (reps, stage, form) directly on the video feed.

## Technologies Used
- **Python 3.8+**: Core programming language.
- **MediaPipe**: For pose estimation and landmark detection.
- **OpenCV**: For video processing and rendering.
- **Streamlit**: For the web-based user interface.
- **streamlit-webrtc**: For real-time webcam streaming.
- **NumPy**: For angle calculations and coordinate processing.

## Installation
Follow these steps to set up the project locally:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mohdalipatel8976/ai-fitness-trainer.git
   cd ai-fitness-trainer


Set Up a Virtual Environment (recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install -r requirements.txt

Verify Webcam Access:Ensure your webcam is connected and accessible. Test with a simple OpenCV script if needed.


Usage

Run the App:
streamlit run app.py


Interact with the App:

Open the provided URL (usually http://localhost:8501) in your browser.
Allow webcam access when prompted.
Position yourself in front of the camera (front or side view) and start doing pushups.
The app will display:
Reps: Number of completed pushups.
Stage: Current pushup phase ("up" or "down").
Form: Feedback on body alignment ("Good" or "Bad - Straighten body").
Warnings: Alerts for improper camera placement or low light.


Click the Reset Counter button to restart the rep count.


Stop the App:Press Ctrl+C in the terminal to stop the Streamlit server.


How It Works
The app leverages MediaPipe's Pose Estimation to detect key body landmarks (shoulders, elbows, hips, etc.) in real-time video frames. Here's a breakdown:

View Detection: Determines if you're in a front or side view based on landmark visibility.
Distance Check: Ensures the camera is positioned correctly by measuring shoulder distance (front view) or torso length (side view).
Form Analysis: Calculates angles between shoulders, hips, and ankles to verify proper body alignment.
Pushup Counting: Tracks elbow angles (side view) or shoulder-elbow height differences (front view) to detect "up" and "down" phases, incrementing the counter for valid pushups with good form.
Rendering: Overlays landmarks, angles, and status information on the video feed using OpenCV.

The Streamlit interface uses streamlit-webrtc to handle webcam streaming and processing, with session state to maintain counter and stage variables across frames.
Project Structure
ai-fitness-trainer/
├── app.py              # Main Streamlit application
├── requirements.txt    # Project dependencies
├── README.md           # Project documentation

Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Make your changes and commit (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a Pull Request with a clear description of your changes.

Please ensure your code follows PEP 8 style guidelines and includes appropriate comments.
License
This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgements

Thanks to the MediaPipe team for their robust pose estimation library.
Streamlit and streamlit-webrtc for making web app development seamless.
OpenCV community for powerful computer vision tools.
Inspired by fitness tech and the potential of AI to enhance everyday activities.


