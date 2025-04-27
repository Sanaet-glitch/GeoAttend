# SmartCampus System Architecture

## Overview

SmartCampus is a modular, web-based attendance management system for educational institutions. It focuses on secure, user-friendly, and fraud-resistant attendance tracking using QR codes and session-specific IP blocking. The system is organized into separate modules for student attendance, faculty management, and system administration.

## System Components

### Core Components

1. **Session Management System**
   - Faculty create class sessions for their courses
   - System generates unique QR codes for each session
   - Manages session lifecycle (start/end)

2. **Attendance Recording System**
   - Students mark attendance by scanning a session QR code and entering their admission number
   - Attendance records are created with timestamps and the submitter's IP address
   - Prevents duplicate attendance marks for the same student and session
   - Enforces session-specific IP blocking to prevent proxy attendance (one attendance per device/network per session)

### User Interfaces

1. **Faculty Dashboard**
   - Create and manage class sessions
   - Monitor attendance in real time
   - View and export attendance reports
   - Review flagged/suspicious attendance records

2. **Student Interface**
   - Scan QR code to mark attendance (no login required)
   - Enter admission number to confirm identity
   - View personal attendance history and course enrollments

3. **Admin Interface**
   - Manage users, courses, and sessions
   - System-wide attendance monitoring and reporting

## Data Flow

1. Faculty creates a class session
2. System generates a unique QR code for the session
3. Student scans the QR code and submits their admission number
4. System checks for duplicate attendance and session-specific IP reuse
5. If checks pass, attendance is recorded; otherwise, an error or flag is raised
6. Faculty and admins can view, filter, and export attendance records

## Security Measures

1. **Anti-Fraud Measures**
   - Session-specific IP address tracking and blocking
   - One attendance per student per session
   - Automated flagging of suspicious patterns (e.g., multiple attempts from same IP)
   - Same-network requirement: Students must be within the same network as the lecturer/faculty to mark attendance (attendance is only accepted if the student's IP matches the network of the faculty/session host)

2. **Data Protection**
   - Minimal personal data collection
   - IP addresses are used only for internal validation and never exposed in reports or UI

## Database Schema

See [DATABASE.md](DATABASE.md) for detailed database schema information.

## API Endpoints

See [API.md](API.md) for comprehensive API documentation.
