#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')  # Changed from 'GeoAttend.settings' to just 'settings'
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    print("To access the server:")
    print("1. On the same machine, use http://127.0.0.1:8000/ or http://localhost:8000/.")
    print("2. On another device in the same network, use http://<your-computer-ip>:8000/ (e.g., http://192.168.1.147:8000/).")
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
