import os
import pytest
import requests
import requests_mock
import buptelecmon.electricitymonitor
import buptelecmon.exceptions

# Login URL
LOGIN_URL = 'https://webapp.bupt.edu.cn/wap/login/commit.html'

# Create the object
em = buptelecmon.electricitymonitor.ElectricityMonitor()

# Test Login Function
# Unable to visit the logging in page because of this page is unreachable
def test_login_with_status_error(requests_mock):
    # Mock an error status code
    requests_mock.post(LOGIN_URL, status_code=500)
    with pytest.raises(requests.exceptions.HTTPError):
        em.login('', '')

# Can visit this logging in page, but the server responses an error
def test_login_with_internal_error(requests_mock):
    # Mock an error response
    requests_mock.post(LOGIN_URL,
        text='{"name":"Internal Server Error","message":"There was an error at the server.","code":0,"status":500}')
    with pytest.raises(buptelecmon.exceptions.RemoteFailed):
        em.login('', '')

# Now the token is wrong
def test_login_with_wrong_token():
    with pytest.raises(buptelecmon.exceptions.LoginFailed):
        em.login('', '')

# Login successfully
def test_login_correctly():
    em.login(os.environ['MENGXIAO_STUDENT_ID'], os.environ['MENGXIAO_PASSWORD'])
