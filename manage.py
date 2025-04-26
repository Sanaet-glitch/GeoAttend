#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
        
    # Only show our custom message if running the server command
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        # Get the local IP address for network access
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Check if a specific IP/port was provided in runserver command
        port = "8000"  # Default port
        if len(sys.argv) > 2:
            parts = sys.argv[2].split(":")
            if len(parts) > 1:
                port = parts[1]
        
        print("\n-------------------------------------------------------")
        print(f"Server running at:")
        print(f"• Local access: http://127.0.0.1:{port}/")
        print(f"• Network access: http://{local_ip}:{port}/")
        print("• For QR code scanning, use the Network access URL")
        print("-------------------------------------------------------\n")
        
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
