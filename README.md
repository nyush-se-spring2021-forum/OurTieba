# OurTieba

## Description:

This system works as a forum, like in China mainland it looks like Baidu Tieba, and in the foreign network it looks like
Reddit. This system allows users to view boards, posts and comments that created by other users and also allows users to
create their own posts and comments. But it is not only a clone of these existing forums. We add a new function in
our system: pushing news to the users from outside websites.

## Contributors:

User670
Juncheng Dong  
Ruhao Xin  
Zihang Xia

## Usage:
**IMPORTANT:** Please user **Python 3.8 or later**, otherwise you will have to find out all walrus operators (:=) in the code and rewrite them with normal logic.  


First unzip the source code. Then follow the instructions as needed below. Make sure working directory is the source
code's directory. For Linux users, please replace "python" in the commands below with "python3".

### To install:

    pip install -r requirements.txt

### To run test:

    python app.py --dev
    pytest

Note: a development server will be running for test with a test database. Default host is localhost, and default port is
5000. Must be the same as in `tests/conftest.py`.

`tests/test_index.py` includes a test that uses Selenium to control a web browser and interact with the web pages.
To use this test, you need to install and configure Selenium Webdriver. More specifically:
- Go to this website to find a driver for your browser: https://www.selenium.dev/downloads/
- In `setup.cfg`, change the `addopts` line, so that the `--driver` parameter matches your browser, and `--driver-path` parameter matches the path of your driver. If you placed your driver executable in your PATH, you may remove this parameter.
- If your browser executable is not in a standard location, or if you need to further specify options for your browser, follow this guide and add options to `tests/conftest.py`: https://pytest-selenium.readthedocs.io/en/latest/user_guide.html#specifying-a-browser

In addition, you may want to edit `tests/test_index.py` to change a few parameters, for example, the host name of the app, and extra waiting time to compensate for lag.  

**IMPORTANT:** test.db will be modified during the test and will not be restored in the end. To manually restore, run:  

    python restore_test_db.py


### To run production server:

    gunicorn app:app -c guni_config.py

Note: production server runs at local broadcast address on port 80 by default. To assign new ones, please modify "bind"
in guni_config.py.

### To generate docstring (for package "ourtieba"):

    python generate_doc.py

Note: a "docs" folder will be created to contain all HTML files generated.
