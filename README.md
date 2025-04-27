# SmartCampus: Smart Attendance System

SmartCampus is a modern, network-based attendance system that uses QR codes and session-specific IP blocking to ensure secure and user-friendly attendance tracking for educational institutions.

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
   source env/bin/activate  # On Windows: env\Scripts\activate
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

## Application Structure

- **Core App**: Basic models (Course, ClassSession)
- **Attendance App**: Student attendance tracking with network/IP verification
- **Faculty App**: Session management and attendance monitoring
- **Administration App**: System management and configuration

## License

This project is open source and available under the [MIT License](LICENSE).
