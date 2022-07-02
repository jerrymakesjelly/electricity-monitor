import os
import pytest
import buptelecmon.electricitymonitor
import buptelecmon.exceptions

# Login URL
LOGIN_URL = 'https://auth.bupt.edu.cn/authserver/login'
EXECUTION_CODE_TEXT = \
    '<input name="execution" value="123"/><input name="_eventId"/>'

# Create the object
em = buptelecmon.electricitymonitor.ElectricityMonitor()

# Test Login Function
# Unable to visit the logging in page because of this page is unreachable
def test_login_with_status_error(requests_mock):
    # Mock an error status code
    requests_mock.get(LOGIN_URL, text=EXECUTION_CODE_TEXT)
    requests_mock.post(LOGIN_URL, status_code=500)
    with pytest.raises(buptelecmon.exceptions.LoginFailed):
        em.login('', '')

# Can visit this logging in page, but the server responses an error
def test_login_with_internal_error(requests_mock):
    # Mock an error response
    requests_mock.get(LOGIN_URL, text=EXECUTION_CODE_TEXT)
    requests_mock.post(LOGIN_URL,
        text='{"name":"Internal Server Error","message":"There was an error at the server.","code":0,"status":500}')
    with pytest.raises(buptelecmon.exceptions.LoginFailed):
        em.login('', '')

# Now the token is wrong
def test_login_with_wrong_token():
    with pytest.raises(buptelecmon.exceptions.LoginFailed):
        em.login('', '')

# Login successfully
def test_login_correctly():
    em.login(os.environ['MENGXIAO_STUDENT_ID'], os.environ['MENGXIAO_PASSWORD'])
