# OurTieba

## Usage:
First unzip the source code. Then follow the instructions as needed below. Make sure working directory is the source code's directory.

### To install:
    pip install -r requirements.txt

### To run test:
    python app.py --dev
    pytest
Note: default host is localhost, default port is 5000. Must be the same as in tests/conftest.py.

### To run production server:
    gunicorn app:app -c guni_config.py
Note: server default runs at local broadcast address on port 80.