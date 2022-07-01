# -*- coding:utf-8 -*-
import time
import socket
import threading
import requests
import urllib.parse
from datetime import datetime
import re
import buptelecmon.logger
import buptelecmon.exceptions

class ElectricityMonitor(object):
    _logger = buptelecmon.logger.register(__name__)

    def __init__(self):
        self._username = ''
        self._password = ''
        self._session = requests.Session()
        self._session.headers.update({
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
        })
        self._looping = False

    # Login to the service
    def login(self, username, password):
        login_url = 'https://auth.bupt.edu.cn/authserver/login'
        chong_url = 'https://app.bupt.edu.cn/buptdf/wap/default/chong'

        self._logger.debug('Logging in.')
        res = self._session.get(login_url)
        execution = re.findall(r'input name="execution" value="(.*)"/><input name="_eventId"', str(res.content))[0]

        login_form = {
            'submit': "LOGIN",
            'type': "username_password",
            '_eventId': "submit",
            'username': username,
            'password': password,
            'execution': execution,
        }

        # get login cookies
        res = self._session.post(login_url, data=login_form, allow_redirects=False)
        if res.status_code != requests.codes.found: # 302 is the expected code
            raise buptelecmon.exceptions.RemoteError('Login failed.')

        # get chong cookies
        res = self._session.post(chong_url, allow_redirects=True)
        if res.status_code == requests.codes.found: # 302 is the expected code
            raise buptelecmon.exceptions.RemoteError('Login failed.')

        self._logger.debug('Login successful.')
            

    # Send a query
    def _query(self, url, data=None):
        self._logger.debug('Getting data from '+str(url)+' ['+str(data)+'].')
        res = self._session.post(url, allow_redirects=False, data=data)
        if res.status_code == requests.codes.ok:
            response = res.json()
            if 'e' in response and response['e'] == 0:
                if 'd' in response:
                    self._logger.debug('Getting data from '+str(url)+' is successful.')
                    return response['d'] # success
                else:
                    raise buptelecmon.exceptions.RemoteError('Bad response.')
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
    def get_part_list(self, areaid):
        part_url = 'https://app.bupt.edu.cn/buptdf/wap/default/part'
        return self._query(part_url, data={'areaid': str(areaid)})['data']
    
    # Get floor list by partment ID
    def get_floor_list(self, areaid, partmentId):
        floor_url = 'https://app.bupt.edu.cn/buptdf/wap/default/floor'
        return self._query(floor_url, {'areaid':str(areaid), 'partmentId':partmentId})['data']

    # Get dormitory list by partmentID and floor ID
    def get_dorm_list(self, areaid, partmentId, floorId):
        dorm_url = 'https://app.bupt.edu.cn/buptdf/wap/default/drom'
        return self._query(dorm_url, {'areaid':str(areaid), 'partmentId':partmentId, 'floorId':str(floorId)})['data']

    # Get electricity data of a dormitory
    def get_electricity_data(self, areaid, partmentId, floorId, dromNumber):
        search_url = 'https://app.bupt.edu.cn/buptdf/wap/default/search'
        return self._query(search_url, {'areaid':str(areaid), 'partmentId':partmentId, 'floorId':str(floorId), 'dromNumber':dromNumber})['data']

    # Get recharging link
    def get_recharge_link(self, dormitory_number):
        parameters = self._convert_partment([dormitory_number])[0]
        values = {
            'partmentId': parameters['partmentId'],
            'floorId': parameters['floor'],
            'dromNumber': parameters['dormitory'],
            'dromName': parameters['dormitory'],
            'partmentName': parameters['partmentName'],
            'areaId': parameters['areaId']
        }
        return 'https://app.bupt.edu.cn/buptdf/wap/recharge/index?%s' % \
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
        result = []
        for dormitory in dormitory_list:
            dormName = dormitory
            parts = dormitory.split('-')
            if len(parts) > 1:
                if parts[0].isnumeric():
                    # Xitucheng Campus
                    areaid = 1 
                    partment_list = self.get_part_list(areaid)
                    partment_name = '学{}楼'.format(self._convert_to_uppercase_number(int(parts[0])))
                else:
                    # Shahe Campus
                    areaid = 2 
                    partment_list = self.get_part_list(areaid)
                    partment_name = parts[0]

                # check if the part number is valid.
                partment_id = ''
                for p in partment_list:
                    if areaid == 1 and p['partmentName'] == partment_name:
                        partment_id = p['partmentId']
                        break
                    elif areaid == 2 and partment_name in p['partmentName']:
                        partment_name = p['partmentName']
                        partment_id = p['partmentId']
                        break

                if partment_id == '':
                    raise buptelecmon.exceptions.PartmentNameNotFound('"'+parts[0]+'" is not in the partment list.')

                # Speclate floor number
                floor = 0
                if len(parts[1]) == 4:
                    if parts[1][0] == 'D': # Negative floor number
                        floor = -int(parts[1][1])
                    else: # Two-digit floor number
                        floor = int(parts[1][0:2])
                elif len(parts[1]) == 3: # One-digit floor number
                    floor = int(parts[1][0])

                if areaid == 2:
                    # If is Shahe Campus, we should get the dormNumber,
                    # and change the floorId
                    floor = str(floor) + '层'
                    dorm_list = self.get_dorm_list(areaid, partment_id, floor)
                    for dorm in dorm_list:
                        if parts[1] in dorm['dromName']:
                            dormitory = dorm['dromNum']
                            break

                result.append({
                    'partmentId': partment_id, 
                    'partmentName': partment_name,
                    'floor': floor, 
                    'dormitory': dormitory,
                    'dormName': dormName,
                    'areaId': areaid
                })
            else:
                raise buptelecmon.exceptions.InvalidDormitoryNumber('"'+dormitory+'" is not a valid dormitory number.')
        return result

    # Query thread
    def _query_thread(self, areaid, partment, floor, dormitory, dormName, succeed_callback):
        for _ in range(3):
            try:
                data = self.get_electricity_data(areaid, partment, floor, dormitory)
                data['areaid'] = areaid
                data['dormName'] = dormName
                succeed_callback(dormitory, data)
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
                args=(dormitory['areaId'], dormitory['partmentId'], dormitory['floor'], dormitory['dormitory'], dormitory['dormName'],
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
                callback_function(results[dormitory], params)
            end_time = datetime.now()
            # Fix request time
            fix_interval = (end_time - start_time).total_seconds()
            if fix_interval < time_interval:
                time.sleep(time_interval - fix_interval)

    # Stop looping function
    def stop_looping(self):
        self._looping = False