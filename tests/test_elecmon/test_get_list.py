import os
import pytest
import requests
import requests_mock
import buptelecmon.electricitymonitor
import buptelecmon.exceptions

# URL of Getting Partment
PARTMENT_URL = 'https://webapp.bupt.edu.cn/w_dianfei/default/part'

# Create object
em = buptelecmon.electricitymonitor.ElectricityMonitor()

# HTTP Error
def test_query_with_http_error(requests_mock):
    requests_mock.post(PARTMENT_URL, status_code=500)
    with pytest.raises(requests.exceptions.HTTPError):
        em.get_part_list()

# Before logging in
def test_query_before_login():
    with pytest.raises(buptelecmon.exceptions.NeedLogin):
        em.get_part_list()

# Internal Error
def test_query_with_internal_error():
    # Login
    em.login(os.environ['MENGXIAO_STUDENT_ID'], os.environ['MENGXIAO_PASSWORD'])
    # Test
    with pytest.raises(buptelecmon.exceptions.RemoteError):
        em.get_floor_list('abc')

# Successful Tests
def test_part_list():
    em.get_part_list()

def test_floor_list_correctly():
    em.get_floor_list(os.environ['MENGXIAO_TEST_PARTMENT'])

def test_dorm_list_correctly():
    em.get_dorm_list(os.environ['MENGXIAO_TEST_PARTMENT'], os.environ['MENGXIAO_TEST_FLOOR'])

def test_dorm_list_unsuccessfully():
    with pytest.raises(buptelecmon.exceptions.RemoteError):
        em.get_dorm_list('def', 'ghi')

def test_electricity_data_correctly():
    em.get_electricity_data(os.environ['MENGXIAO_TEST_PARTMENT'],
        os.environ['MENGXIAO_TEST_FLOOR'], os.environ['MENGXIAO_TEST_DORMITORY'])

def test_electricity_data_with_non_existed_dormitory():
    with pytest.raises(buptelecmon.exceptions.RemoteError):
        em.get_electricity_data('jkl', 'mno', 'pqr')