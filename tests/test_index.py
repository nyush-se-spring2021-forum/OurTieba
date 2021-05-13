import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

#
# def test_login(selenium):
#     selenium.get('http://localhost:80/')
#     selenium.find_element_by_link_text('Login').click()
#     time.sleep(2)
#     assert selenium.current_url == 'http://localhost/login'
#     username = selenium.find_element_by_id('uname')
#     username.send_keys('U1')
#     password = selenium.find_element_by_id('password')
#     password.send_keys('111')
#     selenium.find_element_by_id('btn_submit').click()
#     time.sleep(1)
#     assert selenium.current_url == 'http://localhost/'


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
    selenium.get('http://localhost/board/1')
    assert selenium.current_url == 'http://localhost/board/1'
    cookie = str(random.randint(0, 1000000))
    title = selenium.find_element_by_id('title')
    title.send_keys('What I love' + cookie)
    selenium.switch_to.frame('ueditor_0')
    content = selenium.find_element_by_tag_name('body')
    content.send_keys('I love software engineering' + cookie)
    selenium.switch_to.default_content()
    time.sleep(1)
    selenium.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.CONTROL, Keys.END);
    submit = selenium.find_element_by_xpath('/html/body/div[1]/div/div[13]/div[3]/div/button[1]')
    submit.click()
    time.sleep(2)
    assert cookie in selenium.page_source
