import os
import time
import threading
import pytest
import mock
import requests_mock
import json
import buptelecmon.electricitymonitor
import buptelecmon.exceptions

em = buptelecmon.electricitymonitor.ElectricityMonitor()
em.login(os.environ['MENGXIAO_STUDENT_ID'], os.environ['MENGXIAO_PASSWORD'])

def test_convertion_correcyly():
    cases = {
        '1-999': ('学一楼', 9),
        '13-1526': ('学十三楼', 15),
        '29-D999': ('学二十九楼', -9),
        '6-111-11': ('学六楼', 1)
    }
    results = em._convert_partment([x for x in cases])
    for result in results:
        assert result['partmentName'] == cases[result['dormitory']][0]
        assert result['floor'] == cases[result['dormitory']][1]

def test_query_with_wrong_format():
    with pytest.raises(buptelecmon.exceptions.InvalidDormitoryNumber):
        em.query(['abc'])

def test_query_with_invalid_partment():
    with pytest.raises(buptelecmon.exceptions.InvalidDormitoryNumber):
        em.query(['a-bcd-efg-hij'])

def test_query_with_outbound_partment():
    with pytest.raises(buptelecmon.exceptions.PartmentNameNotFound):
        em.query(['100-999'])

def test_query_with_non_existed_partment():
    with pytest.raises(buptelecmon.exceptions.PartmentNameNotFound):
        em.query(['12-888'])

def test_query_correctly(test_dormitories):
    dormitory_list = test_dormitories
    results = em.query(dormitory_list)
    with open('test_query_result.json', 'w', encoding='utf-8') as fp:
        json.dump(results, fp)
    assert len(dormitory_list) == len(results)

def test_query_with_non_existed_dormitory():
    em.query(['1-000'])

def test_loop(test_dormitories):
    def _test_loop_thread():
        time.sleep(5)
        em.stop_looping()
    with open('test_query_result.json', 'r') as fp:
        results = json.load(fp)
    trd = threading.Thread(target=_test_loop_thread)
    trd.start()
    with mock.patch('buptelecmon.electricitymonitor.ElectricityMonitor.query', return_value=results) as moc, \
        mock.patch('time.sleep'):
        em.loop(test_dormitories, lambda d, r, p: None)
        moc.assert_called_with(test_dormitories)
        assert moc.call_count > 1
    trd.join()
    return results
