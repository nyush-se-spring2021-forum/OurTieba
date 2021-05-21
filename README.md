# OurTieba
## Description:
This system works as a forum, like in China mainland it looks like Baidu Tieba, and in the foreign network it looks like Reddit. This system allows users to view boards, posts and comments that created by other users and also allows users to create their own posts and comments. But it is not only a duplicate of these existing forums. We add a new function in our system: pushing news to the users from outside websites. 

## Contributors:
Boyan Li
Juncheng Dong
Ruhao Xin
Zihang Xia

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
