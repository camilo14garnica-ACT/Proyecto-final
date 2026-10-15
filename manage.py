#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def check_and_use_venv():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, '.venv', 'Scripts', 'python.exe'),
        os.path.join(base_dir, '.venv', 'bin', 'python'),
        os.path.join(base_dir, 'venv', 'Scripts', 'python.exe'),
        os.path.join(base_dir, 'venv', 'bin', 'python'),
    ]
    for venv_py in candidates:
        if os.path.exists(venv_py):
            try:
                if os.path.samefile(sys.executable, venv_py):
                    return
            except (AttributeError, OSError):
                if os.path.abspath(sys.executable).lower() == os.path.abspath(venv_py).lower():
                    return
            import subprocess
            sys.exit(subprocess.call([venv_py] + sys.argv))


def main():
    """Run administrative tasks."""
    check_and_use_venv()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
