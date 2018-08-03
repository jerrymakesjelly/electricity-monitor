import sys
import os
import signal
import time
import json
import threading
import mock
from contextlib import contextmanager
from io import StringIO
import buptelecmon.main
import buptelecmon.configurationmanager

def test_remaining_time_convertion():
    assert buptelecmon.main.convert_rat(26.0512) == '1day(s) 02:03:04'

def test_set_auth():
    # Replace stdin for mocking
    # Thanks to https://stackoverflow.com/a/36491341
    @contextmanager
    def replace_stdin(target): 
        ori = sys.stdin
        sys.stdin = target
        yield
        sys.stdin = ori
    # Test code
    username = os.environ['MENGXIAO_STUDENT_ID']
    password = os.environ['MENGXIAO_PASSWORD']
    with replace_stdin(StringIO('%s\n%s\n' % (username, password))):
        buptelecmon.main.main(['--set-auth'])
    # Read config
    cm = buptelecmon.configurationmanager.ConfigMan('elecmon', 'elecmon.json')
    result = cm.read()
    assert result['username'] == username and result['password'] == password

def test_once_mode(test_dormitories):
    # Sub process
    def _sub_test_once_mode(use_parameter):
        with open('test_query_result.json', 'r') as fp:
            results = json.load(fp)
        with mock.patch('buptelecmon.electricitymonitor.ElectricityMonitor.query', return_value=results) as moc:
            buptelecmon.main.main(test_dormitories if use_parameter else [])
            moc.assert_called_with(test_dormitories)
    # Test Exceptions
    with mock.patch('buptelecmon.electricitymonitor.ElectricityMonitor.query',
        side_effect=RuntimeError):
        buptelecmon.main.main(['6-699'])
    # Test with parameters
    _sub_test_once_mode(True)
    # Test with no parameter
    _sub_test_once_mode(False)

def test_loop_mode(test_dormitories):
    # Sub test process
    def _sub_test_loop_mode(use_parameter):
        with mock.patch('buptelecmon.electricitymonitor.ElectricityMonitor.loop', 
            side_effect=KeyboardInterrupt) as moc:
            buptelecmon.main.main(['--loop', test_dormitories[0]] if use_parameter
                else ['--loop'])
            moc.assert_called_with([test_dormitories[0]], buptelecmon.main.output)
    # Test with parameters
    _sub_test_loop_mode(True)
    # Test with no parameter
    _sub_test_loop_mode(False)

def test_main_function():
    with mock.patch('buptelecmon.main.main'):
        buptelecmon.main.init('__main__')
