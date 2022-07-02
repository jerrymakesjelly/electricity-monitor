import os
import pytest
import requests
import requests_mock
import buptelecmon.electricitymonitor
import buptelecmon.exceptions

# URL of Getting Partment
PARTMENT_URL = 'https://app.bupt.edu.cn/buptdf/wap/default/part'

TEST_USERNAME = os.environ['MENGXIAO_STUDENT_ID']
TEST_PASSWORD = os.environ['MENGXIAO_PASSWORD']
TEST_CAMPUS = 1
TEST_PARTMENT = 'f8067fcf9c4f48c6b2f8e793d64b7b65'
TEST_FLOOR = '1'
TEST_DORMITORY = '1-111'

# Please note,
# setting campus to an unexpected value won't result in RemoteError,
# but other fields will.

# Create object
em = buptelecmon.electricitymonitor.ElectricityMonitor()

# HTTP Error
def test_query_with_http_error(requests_mock):
    requests_mock.post(PARTMENT_URL, status_code=500)
    with pytest.raises(requests.exceptions.HTTPError):
        em.get_part_list(TEST_CAMPUS)

# Before logging in
def test_query_before_login():
    with pytest.raises(buptelecmon.exceptions.NeedLogin):
        em.get_part_list(TEST_CAMPUS)

# Internal Error
def test_query_with_internal_error():
    # Login
    em.login(TEST_USERNAME, TEST_PASSWORD)
    # Test
    with pytest.raises(buptelecmon.exceptions.RemoteError):
        em.get_floor_list(TEST_CAMPUS, 'abc')

# Successful Tests
def test_part_list():
    em.get_part_list(TEST_CAMPUS)

def test_floor_list_correctly():
    em.get_floor_list(TEST_CAMPUS, TEST_PARTMENT)

def test_dorm_list_correctly():
    em.get_dorm_list(TEST_CAMPUS, TEST_PARTMENT, TEST_FLOOR)

def test_dorm_list_unsuccessfully():
    with pytest.raises(buptelecmon.exceptions.RemoteError):
        em.get_dorm_list('1', 'def', 'ghi')

def test_electricity_data_correctly():
    em.get_electricity_data(TEST_CAMPUS, TEST_PARTMENT,
        TEST_FLOOR, TEST_DORMITORY)

def test_electricity_data_with_non_existed_dormitory():
    with pytest.raises(buptelecmon.exceptions.RemoteError):
        em.get_electricity_data('1', 'jkl', 'mno', 'pqr')

def test_recharge_link(test_dormitories):
    em.get_recharge_link(test_dormitories[0])