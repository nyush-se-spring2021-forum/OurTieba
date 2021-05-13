import time

from flask import url_for


def test_login(selenium):
    selenium.get('http://localhost:80/')
    selenium.find_element_by_link_text('Login').click()
    time.sleep(2)
    assert selenium.current_url == 'http://localhost/login'
    username = selenium.find_element_by_id('uname')
    username.send_keys('U1')
    password = selenium.find_element_by_id('password')
    password.send_keys('111')
    selenium.find_element_by_id('btn_submit').click()
    time.sleep(1)
    assert selenium.current_url == 'http://localhost/'


# def test_logout(selenium):
#     selenium.get('http//localhost:80/')
#     selenium.find_element_by_partial_link_text('Sign').click()
#     assert selenium.find_element_by_link_text('Login') is not None
#     print('*'*100)

def test_comment(selenium):
    selenium.get('http://localhost:80/')
    selenium.find_element_by_link_text('Login').click()
    time.sleep(2)
    assert selenium.current_url == 'http://localhost/login'
    username = selenium.find_element_by_id('uname')
    username.send_keys('U1')
    password = selenium.find_element_by_id('password')
    password.send_keys('111')
    selenium.find_element_by_id('btn_submit').click()
    time.sleep(1)
    assert selenium.current_url == 'http://localhost/'
    selenium.get('http://localhost/post/1')
    assert selenium.current_url == 'http://localhost/post/1'
