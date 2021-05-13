import pytest

@pytest.fixture
def selenium(selenium):
    selenium.implicitly_wait(10)
    selenium.maximize_window()
    return selenium
