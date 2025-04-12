# GeoAttend System Architecture

## Overview

GeoAttend is built on a modular architecture that separates concerns between student attendance, faculty management, and system administration.

## System Components

### Core Components

1. **Session Management System**
   - Creates class sessions with location data
   - Generates unique QR codes for each session
   - Manages session lifecycle (start/end)

2. **Geolocation Verification System**
   - Captures student GPS coordinates
   - Calculates distance from class location
   - Verifies presence within specified radius

3. **Attendance Recording System**
   - Maintains attendance records with timestamps
   - Tracks verification method and status
   - Prevents duplicate attendance marks

### User Interfaces

1. **Faculty Dashboard**
   - Session creation and management
   - Real-time attendance monitoring
   - Historical attendance reports
   - Flagged attendance review

2. **Student Interface**
   - QR code scanning
   - Location permission handling
   - Attendance confirmation

3. **Admin Interface**
   - User management
   - Course setup and configuration
   - System monitoring and reports

## Data Flow

1. Faculty creates a class session, capturing location coordinates
2. System generates unique QR code for the session
3. Student scans QR code with mobile device browser
4. Browser requests permission to access location
5. System verifies student location against class location
6. If within radius, attendance is marked as verified
7. Faculty sees real-time update on dashboard

## Security Measures

1. **Location Verification**
   - GPS coordinate validation
   - Configurable proximity radius
   - Distance calculation with Haversine formula

2. **Anti-Fraud Measures**
   - IP address tracking
   - One attendance per session
   - Automated flagging of suspicious patterns

3. **Data Protection**
   - Minimal personal data collection
   - Location data used only for verification
   - No permanent storage of coordinates

## Database Schema

See [DATABASE.md](DATABASE.md) for detailed database schema information.

## API Endpoints

See [API.md](API.md) for comprehensive API documentation.
