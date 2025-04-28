# SmartCampus: Smart Attendance System

SmartCampus is a modern, network-based attendance system that uses QR codes and session-specific IP blocking to ensure secure and user-friendly attendance tracking for educational institutions.

## Project Overview

SmartCampus streamlines attendance for students and faculty by leveraging QR codes and network-based verification. The system is designed to prevent attendance fraud, provide real-time monitoring, and offer a seamless experience for all users.

## My Role & Contributions

- Designed and implemented core backend logic (Django)
- Developed anti-fraud features (IP tracking, same-network enforcement)
- Built and integrated QR code generation and scanning workflows
- Created real-time attendance monitoring for faculty
- Wrote documentation and setup instructions

## Core Features

- **Simple Student Experience**: Just scan a QR code - no login required
- **Anti-Proxy Measures**: Prevents attendance fraud through session-specific IP tracking and same-network enforcement
- **Real-time Monitoring**: Faculty can see attendance updates instantly
- **Cloud-Ready Architecture**: Deployable to any cloud platform

## Technology Stack

- **Backend**: Django/Django REST Framework
- **Frontend**: HTML5, CSS3, JavaScript
- **Security**: IP tracking, device fingerprinting

## Getting Started

### Prerequisites

- Python 3.8+
- Git

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/YOUR-USERNAME/SmartCampus.git
   cd SmartCampus
   ```
2. Create and activate a virtual environment:
   ```
   python -m venv env
   env\Scripts\activate  # On Windows
   # On Mac/Linux: source env/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```
   python manage.py migrate
   ```
5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```
   python manage.py runserver
   ```
7. Access the application at http://localhost:8000

## Accessing the Application on Other Devices (for Demo & Testing)

To allow other devices on your local network (e.g., students' phones) to access the application and mark attendance via QR code, follow these steps:

1. **Find your local IP address:**
   - Open Command Prompt and run:
     ```
     ipconfig
     ```
   - Look for the `IPv4 Address` under your active network adapter (e.g., `192.168.1.5`).

2. **Run the Django server on all interfaces:**
   - Start the server with:
     ```
     python manage.py runserver 0.0.0.0:8000
     ```
   - This makes your app accessible at `http://<your-ip>:8000` from other devices on the same Wi-Fi/network.

3. **Access the faculty dashboard/session page using your local IP:**
   - In your browser, go to `http://<your-ip>:8000` (not `localhost`).
   - When you create a session, the QR code will now contain the correct network-accessible URL.

4. **Students scan the QR code:**
   - Students' devices will be able to access the attendance marking page using the QR code, as long as they are on the same network.

> **Note:** If you use `localhost` in your browser, the QR code will embed `localhost`, which will not work for other devices. Always use your local IP for multi-device testing or demos.

## Demo Instructions

- **Faculty**: Log in, create a session, and display the QR code for students.
- **Student**: Scan the QR code using a mobile device on the same network to mark attendance.
- **Admin**: Use the admin dashboard to monitor and manage attendance records.

## Application Structure

- **Core App**: Basic models (Course, ClassSession)
- **Attendance App**: Student attendance tracking with network/IP verification
- **Faculty App**: Session management and attendance monitoring
- **Administration App**: System management and configuration

## Technical Highlights & Challenges

- Session-specific QR code generation and validation
- IP address and network-based attendance verification
- Real-time updates for faculty dashboards
- Security measures to prevent proxy/VPN-based fraud

## License

This project is open source and available under the [MIT License](LICENSE).
