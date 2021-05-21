import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

'''
Comments from User670:
Yes, this is a very long test case, probably longer than
ideal. However, part of the case relies on previous
actions (eg, to delete a post, you need a post in then
first place, which here I created beforehand).
If I had to write the test in separate, small chunks,
then I would need some way to set up a state that I need,
which requires some setup scripts or set a pre-built
database to setup the base conditions, which complicates
things further.
'''


def test_comment(selenium):
    """
    This test uses Selenium to emulate user inputs in a
    browser.
    In order for it to work, you need to install Selenium
    WebDriver for your browser, as well as make any
    necessary configurations in conftest.py, and then
    run the server before you run pytest.
    You might also need to adjust the variables at the
    beginning of this test.
    """
    # Change this if your server is hosted at a different
    # URL.
    HOSTNAME = "http://localhost:5000/"

    USERNAME1 = "TestUser" + str(random.randint(1000000, 1999999))
    USERNAME2 = "TestUser" + str(random.randint(2000000, 2999999))
    BAD_PASSWORD = "12345678"
    GOOD_PASSWORD = "Abcd1234!"
    ADMIN_USERNAME = "root"
    ADMIN_PASSWORD = "root"

    # Number of additional seconds to wait for each page
    # load. Should be unnecessary if on localhost (the code
    # below already waits 1 or 2 seconds), but in case the
    # machine is slow or server is remote, this number can be
    # set to some positive value to wait for longer.
    LAG_COMPENSATION = 0

    # Load homepage
    selenium.get(HOSTNAME)
    # Verify home page
    assert selenium.current_url == HOSTNAME
    assert "Hot Boards" in selenium.page_source

    # Register a new user
    selenium.find_element_by_link_text('Register').click()
    time.sleep(2 + LAG_COMPENSATION)
    assert selenium.current_url == HOSTNAME + 'register'
    assert "Join OurTieba" in selenium.page_source

    selenium.find_element_by_id('uname').send_keys(USERNAME1)
    selenium.find_element_by_id('nickname').send_keys(USERNAME1)
    selenium.find_element_by_id('password').send_keys(GOOD_PASSWORD)
    selenium.find_element_by_id('repeat-password').send_keys(GOOD_PASSWORD)
    selenium.find_element_by_id('btn_submit').click()
    time.sleep(2 + LAG_COMPENSATION)
    # Verify registration
    # After registration done, page should be redirected
    # to home page, with "New Messages" indicating it's
    # logged in rather than guest
    assert selenium.current_url == HOSTNAME
    assert "New Messages" in selenium.page_source

    # Create a post in board 1
    selenium.get(HOSTNAME + "board/1")
    time.sleep(2 + LAG_COMPENSATION)
    post_title = "Test post created by Selenium " + str(random.randint(0, 1999999))
    post_content = "This post is created by an automated test using Selenium. " + str(random.randint(0, 1999999))
    selenium.find_element_by_id('title').send_keys(post_title)
    selenium.switch_to.frame('ueditor_0')
    element_ueditor_textbox = selenium.find_element_by_tag_name('body')
    element_ueditor_textbox.send_keys(post_content)
    selenium.switch_to.default_content()
    time.sleep(1)
    selenium.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.CONTROL, Keys.END);
    time.sleep(1)
    elements_buttons = selenium.find_elements_by_tag_name("button")
    for i in elements_buttons:
        if i.text == "Add Post":
            i.click()
            break
    time.sleep(2 + LAG_COMPENSATION)
    # Verify post creation
    # (Now the browser should still be on the board page)
    assert post_title in selenium.page_source
    assert post_content in selenium.page_source
    selenium.find_element_by_link_text(post_title).click()
    time.sleep(2 + LAG_COMPENSATION)
    assert selenium.current_url.startswith(HOSTNAME + "post/")
    assert post_title in selenium.page_source
    assert post_content in selenium.page_source
    # Delete this post
    elements_buttons = selenium.find_elements_by_tag_name("button")
    for i in elements_buttons:
        if i.text == "Delete Post":
            i.click()
            break
    time.sleep(2 + LAG_COMPENSATION)
    elements_buttons = selenium.find_elements_by_tag_name("button")
    for i in elements_buttons:
        if i.text == "Delete":
            i.click()
            break
    time.sleep(2 + LAG_COMPENSATION)
    # Now it should be back to the board page, and the post is gone
    assert selenium.current_url == HOSTNAME + "board/1"
    assert post_title not in selenium.page_source
    assert post_content not in selenium.page_source

    # Create another post.
    post_title = "Test post created by Selenium " + str(random.randint(0, 1999999))
    post_content = "This post is created by an automated test using Selenium. " + str(random.randint(0, 1999999))
    selenium.find_element_by_id('title').send_keys(post_title)
    selenium.switch_to.frame('ueditor_0')
    element_ueditor_textbox = selenium.find_element_by_tag_name('body')
    element_ueditor_textbox.send_keys(post_content)
    selenium.switch_to.default_content()
    time.sleep(1)
    selenium.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.CONTROL, Keys.END);
    time.sleep(1)
    elements_buttons = selenium.find_elements_by_tag_name("button")
    for i in elements_buttons:
        if i.text == "Add Post":
            i.click()
            break
    time.sleep(2 + LAG_COMPENSATION)
    assert post_title in selenium.page_source
    assert post_content in selenium.page_source
    selenium.find_element_by_link_text(post_title).click()
    time.sleep(2 + LAG_COMPENSATION)
    assert selenium.current_url.startswith(HOSTNAME + "post/")
    # The post ID is saved, we will come back to this later
    post_id = selenium.current_url.split("/")[-1]

    # Log out of the first user
    selenium.find_element_by_xpath("/html/body/header/div/div/div/div/a").click()
    selenium.find_element_by_link_text("Sign out").click()
    time.sleep(2 + LAG_COMPENSATION)
    assert "New Messages" not in selenium.page_source

    # Register another user, but test invalid data first
    selenium.find_element_by_link_text('Register').click()
    time.sleep(2 + LAG_COMPENSATION)
    assert selenium.current_url == HOSTNAME + 'register'
    # test creating a user with existing username
    selenium.find_element_by_id('uname').send_keys(USERNAME1)
    selenium.find_element_by_id('nickname').send_keys(USERNAME1)
    selenium.find_element_by_id('password').send_keys(GOOD_PASSWORD)
    selenium.find_element_by_id('repeat-password').send_keys(GOOD_PASSWORD)
    selenium.find_element_by_id('btn_submit').click()
    time.sleep(2 + LAG_COMPENSATION)
    assert "User already exists." in selenium.page_source
    # test creating a user with a weak password
    selenium.refresh()
    time.sleep(2 + LAG_COMPENSATION)
    selenium.find_element_by_id('uname').send_keys(USERNAME2)
    selenium.find_element_by_id('nickname').send_keys(USERNAME2)
    selenium.find_element_by_id('password').send_keys(BAD_PASSWORD)
    selenium.find_element_by_id('repeat-password').send_keys(BAD_PASSWORD)
    selenium.find_element_by_id('btn_submit').click()
    time.sleep(2 + LAG_COMPENSATION)
    assert "Invalid password." in selenium.page_source
    # test creating a user with password that don't match
    selenium.refresh()
    time.sleep(2 + LAG_COMPENSATION)
    selenium.find_element_by_id('uname').send_keys(USERNAME2)
    selenium.find_element_by_id('nickname').send_keys(USERNAME2)
    selenium.find_element_by_id('password').send_keys(GOOD_PASSWORD + "1")
    selenium.find_element_by_id('repeat-password').send_keys(GOOD_PASSWORD)
    selenium.find_element_by_id('btn_submit').click()
    time.sleep(2 + LAG_COMPENSATION)
    assert "Passwords don't match." in selenium.page_source
    # finally, create the account for real
    selenium.refresh()
    time.sleep(2 + LAG_COMPENSATION)
    selenium.find_element_by_id('uname').send_keys(USERNAME2)
    selenium.find_element_by_id('nickname').send_keys(USERNAME2)
    selenium.find_element_by_id('password').send_keys(GOOD_PASSWORD)
    selenium.find_element_by_id('repeat-password').send_keys(GOOD_PASSWORD)
    selenium.find_element_by_id('btn_submit').click()
    time.sleep(2 + LAG_COMPENSATION)

    # Go back to the post from earlier
    selenium.get(HOSTNAME + "post/" + post_id)
    time.sleep(2 + LAG_COMPENSATION)

    # Like, dislike, undislike
    element_like_button = selenium.find_element_by_id("pl-" + post_id)
    element_dislike_button = selenium.find_element_by_id("pd-" + post_id)
    element_like_button.click()
    time.sleep(2 + LAG_COMPENSATION)
    assert element_like_button.text == "1"
    element_dislike_button.click()
    time.sleep(2 + LAG_COMPENSATION)
    assert element_like_button.text == "0"
    assert element_dislike_button.text == "1"
    element_dislike_button.click()
    time.sleep(2 + LAG_COMPENSATION)
    assert element_dislike_button.text == "0"

    # post a reply
    reply_content = "This reply is created by an automated test using Selenium. " + str(random.randint(0, 1999999))
    selenium.switch_to.frame('ueditor_0')
    selenium.find_element_by_tag_name('body').send_keys(reply_content)
    selenium.switch_to.default_content()
    selenium.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.CONTROL, Keys.END);
    time.sleep(1)
    elements_buttons = selenium.find_elements_by_tag_name("button")
    for i in elements_buttons:
        if i.text == "Comment":
            i.click()
            break
    time.sleep(2 + LAG_COMPENSATION)
    assert reply_content in selenium.page_source

    # file a report
    # Keeping a window handle for reference
    tab_handle_post = selenium.current_window_handle
    elements_buttons = selenium.find_elements_by_tag_name("div")
    for i in elements_buttons:
        if i.text == "Report":
            # Yes, there will be multiple report buttons.
            # This clicks on the first, i.e. reporting the post.
            i.click()
            break
    time.sleep(2 + LAG_COMPENSATION)
    # This should open a *new tab* to handle the report.
    tab_handles_all = selenium.window_handles
    for i in tab_handles_all:
        if i != tab_handle_post:
            selenium.switch_to.window(i)
            break
    time.sleep(1)
    report_reason = "This report is filed from Selenium " + str(random.randint(0, 1999999))
    selenium.find_element_by_id("r-reason").send_keys(report_reason)
    selenium.find_element_by_id("report-submit").click()
    time.sleep(2 + LAG_COMPENSATION)
    selenium.switch_to.alert.accept()
    time.sleep(2 + LAG_COMPENSATION)
    # Accepting the alert() will close the tab. Now return to
    # the previous tab
    selenium.switch_to.window(tab_handle_post)
    time.sleep(1)

    # Log out, again
    selenium.find_element_by_xpath("/html/body/header/div/div/div/div/a").click()
    selenium.find_element_by_link_text("Sign out").click()
    time.sleep(2 + LAG_COMPENSATION)
    assert "New Messages" not in selenium.page_source

    # Login as the first user
    selenium.find_element_by_link_text('Login').click()
    time.sleep(2 + LAG_COMPENSATION)
    selenium.find_element_by_id('uname').send_keys(USERNAME1)
    selenium.find_element_by_id('password').send_keys(GOOD_PASSWORD)
    selenium.find_element_by_id('btn_submit').click()
    time.sleep(2 + LAG_COMPENSATION)

    # There should be a non-zero number of notifications
    # for this user. Two, actually, one for the like, one
    # for the reply.
    msg_count_text = selenium.find_element_by_id("new_message").text
    assert msg_count_text.startswith("New Messages: ")
    assert msg_count_text != "New Messages: 0"

    # Go to admin control panel
    selenium.get(HOSTNAME + "admin")
    time.sleep(2 + LAG_COMPENSATION)
    assert selenium.current_url == HOSTNAME + "admin/login"
    selenium.find_element_by_id('aname').send_keys(ADMIN_USERNAME)
    selenium.find_element_by_id('password').send_keys(ADMIN_PASSWORD)
    selenium.find_element_by_id('btn_submit').click()
    time.sleep(2 + LAG_COMPENSATION)
    assert selenium.current_url == HOSTNAME + "admin/dashboard"
    assert "postID: " + post_id in selenium.page_source
    assert report_reason in selenium.page_source

    # Delete the post in question, and resolve the report
    element_post_id = selenium.find_element_by_id("Pid")
    element_post_id.send_keys(post_id)
    selenium.find_element_by_xpath("/html/body/div/div[2]/div[2]/div/div/button[1]").click()
    time.sleep(3 + LAG_COMPENSATION)
    selenium.switch_to.alert.accept()
    selenium.switch_to.default_content()
    time.sleep(1)
    elements_buttons = selenium.find_elements_by_tag_name("button")
    for i in elements_buttons:
        if i.text == "Resolve":
            i.click()
            break
    time.sleep(3 + LAG_COMPENSATION)
    selenium.switch_to.alert.accept()
    selenium.switch_to.default_content()
    time.sleep(3 + LAG_COMPENSATION)
    # clicking the resolve button reloads the page...
    # or it's supposed to.
    selenium.refresh()
    time.sleep(3 + LAG_COMPENSATION)
    # assert report_reason not in selenium.page_source

    # check the post that we deleted is deleted
    selenium.get(HOSTNAME + "posts/" + post_id)
    time.sleep(2 + LAG_COMPENSATION)
    assert "Page Not Found" in selenium.page_source
    time.sleep(3)
