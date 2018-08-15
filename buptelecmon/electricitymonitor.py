# -*- coding:utf-8 -*-
import time
import socket
import threading
import requests
import urllib.parse
from datetime import datetime
import buptelecmon.logger
import buptelecmon.exceptions

class ElectricityMonitor(object):
    _logger = buptelecmon.logger.register(__name__)

    def __init__(self):
        self._username = ''
        self._password = ''
        self._session = requests.Session()
        self._session.headers.update({
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With':'XMLHttpRequest'
        })
        self._looping = False

    # Login to the service
    def login(self, username, password):
        commit_url = 'https://webapp.bupt.edu.cn/wap/login/commit.html'
        self._logger.debug('Logging in.')
        res = self._session.post(commit_url, data={'username':username, 'password':password})
        if res.status_code == requests.codes.ok:
            response = res.json()
            if 'e' in response: # Login Response
                if response['e'] == '9999':
                    self._logger.debug('Login successful.')
                else:
                    raise buptelecmon.exceptions.LoginFailed(response['m'])
            else: # Error Response
                raise buptelecmon.exceptions.RemoteError(
                    str(response['status'])+' '+response['name'] if 'status' in response
                    else 'The remote server has encountered an error.', res.text
                )
        else:
            res.raise_for_status()

    # Send a query
    def _query(self, url, data=None):
        self._logger.debug('Getting data from '+str(url)+' ['+str(data)+'].')
        res = self._session.post(url, allow_redirects=False, data=data, stream=True)
        if res.status_code == requests.codes.ok:
            response = res.json()
            if 'success' in response and response['success']:
                self._logger.debug('Getting data from '+str(url)+' is successful.')
                return response # success
            else:
                raise buptelecmon.exceptions.RemoteError(
                    str(response['status'])+' '+response['name'] if 'status' in response
                    else 'The remote server has encountered an error.', res.text
                )
        elif res.status_code == requests.codes.found: # 302
            raise buptelecmon.exceptions.NeedLogin('Need to login.')
        else:
            res.raise_for_status()
    
    # Get department list
    def get_part_list(self):
        part_url = 'https://webapp.bupt.edu.cn/w_dianfei/default/part'
        return self._query(part_url)['data']
    
    # Get floor list by partment ID
    def get_floor_list(self, partmentId):
        floor_url = 'https://webapp.bupt.edu.cn/w_dianfei/default/floor'
        return self._query(floor_url, {'partmentId':partmentId})['data']

    # Get dormitory list by partmentID and floor ID
    def get_dorm_list(self, partmentId, floorId):
        dorm_url = 'https://webapp.bupt.edu.cn/w_dianfei/default/drom'
        return self._query(dorm_url, {'partmentId':partmentId, 'floorId':str(floorId)})['data']

    # Get electricity data of a dormitory
    def get_electricity_data(self, partmentId, floorId, dromNumber):
        search_url = 'https://webapp.bupt.edu.cn/w_dianfei/default/search'
        return self._query(search_url, {'partmentId':partmentId, 'floorId':str(floorId), 'dromNumber':dromNumber})['data']

    # Get recharging link
    def get_recharge_link(self, dormitory_number):
        parameters = self._convert_partment([dormitory_number])[0]
        values = {
            'partmentId': parameters['partmentId'],
            'floorId': parameters['floor'],
            'dromNumber': parameters['dormitory'],
            'partmentName': parameters['partmentName']
        }
        return 'https://webapp.bupt.edu.cn/w_dianfei/recharge/index?%s' % \
            urllib.parse.urlencode(values)

    # Convert an arabic numeral to uppercase number
    @staticmethod
    def _convert_to_uppercase_number(number):
        result = ''
        digits = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        if isinstance(number, int) and number // 100 == 0:
            if number // 10 > 0:
                result += (digits[number//10] if number//10 != 1 else '') + digits[10]
            result += digits[number%10]
        return result

    # Speclate its partment ID and floor of a dormitory
    def _convert_partment(self, dormitory_list):
        partment_list = self.get_part_list()
        result = []
        for dormitory in dormitory_list:
            found = False
            parts = dormitory.split('-')
            if len(parts) > 1 and parts[0].isnumeric():
                # Speclate floor number
                floor = 0
                if len(parts[1]) == 4:
                    if parts[1][0] == 'D': # Negative floor number
                        floor = -int(parts[1][1])
                    else: # Two-digit floor number
                        floor = int(parts[1][0:2])
                elif len(parts[1]) == 3: # One-digit floor number
                    floor = int(parts[1][0])
                # Convert Parment
                partmentId = ''
                partmentName = self._convert_to_uppercase_number(int(parts[0]))
                for p in partment_list:
                    if p['partmentName'].find(partmentName) == 1:
                        partmentId = p['partmentId']
                        partmentName = p['partmentName']
                        found = True
                if found: # This partment name can be converted to partment id
                    result.append({
                        'partmentId': partmentId, 'partmentName': partmentName,
                        'floor': floor, 'dormitory': dormitory
                    })
                else:
                    raise buptelecmon.exceptions.PartmentNameNotFound('"'+parts[0]+'" is not in the partment list.')
            else:
                raise buptelecmon.exceptions.InvalidDormitoryNumber('"'+dormitory+'" is not a valid dormitory number.')
        return result

    # Query thread
    def _query_thread(self, partment, floor, dormitory, succeed_callback):
        for attempt in range(3):
            try:
                succeed_callback(dormitory, self.get_electricity_data(partment, floor, dormitory))
                break
            except Exception as e:
                self._logger.error('Querying failure at %s: %s.' % (dormitory, repr(e)))
    
    # Query data for dormitories (once mode)
    def query(self, dormitory_list):
        result = {}
        thread_pool = []
        # Create threads for querying
        dormitories = self._convert_partment(dormitory_list)
        for dormitory in dormitories:
            trd = threading.Thread(target=self._query_thread,
                args=(dormitory['partmentId'], dormitory['floor'], dormitory['dormitory'],
                lambda dorm, data: result.update({dorm: data}),),
                name='%s Pulling Thread' % dormitory['dormitory'])
            trd.start()
            thread_pool.append(trd)
        # Wait for completion
        for trd in thread_pool:
            trd.join()
        return result

    # Query electricity data at a regular interval (loop mode)
    def loop(self, dormitory_list, callback_function, params=None, time_interval=60):
        socket.setdefaulttimeout(time_interval*1.5)
        # Start looping
        self._logger.debug('Start collecting datapoints...')
        self._looping = True
        while self._looping:
            # Start querying
            start_time = datetime.now()
            results = self.query(dormitory_list)
            for dormitory in results:
                callback_function(dormitory, results[dormitory], params)
            end_time = datetime.now()
            # Fix request time
            fix_interval = (end_time - start_time).total_seconds()
            if fix_interval < time_interval:
                time.sleep(time_interval - fix_interval)

    # Stop looping function
    def stop_looping(self):
        self._looping = False