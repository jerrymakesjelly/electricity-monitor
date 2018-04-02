# -*- coding:utf-8 -*-
import time
from datetime import datetime, timedelta
import socket
import json
import logger
import requests
import elecmon.exceptions

class ElectricityMonitor(object):
    def __init__(self, username, password):
        self._username = username
        self._password = password

        self._logger = logger.register(__name__)

        self._session = requests.Session()
        self._session.headers.update({
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With':'XMLHttpRequest'
        })

        try:
            self.log_in()
        except elecmon.exceptions.LoginFailed as e:
            self._logger.warning("Can't log in now: %s. Try again later.", str(e))
            self._logger.debug("TRACEBACK:\n", exc_info=True)
    
    def log_in(self):
        commit_url = 'https://webapp.bupt.edu.cn/wap/login/commit.html'

        self._logger.debug('Logging in.')
        res = self._session.post(commit_url, data={'username':self._username, 'password':self._password})
        if res.status_code == requests.codes.ok:
            response = res.json()
            if 'e' in response: # Login Response
                if response['e'] == '9999':
                    self._logger.debug('Login successful.')
                else:
                    raise elecmon.exceptions.LoginFailed(response['m'])
            else: # Error Response
                if 'status' in response:
                    raise elecmon.exceptions.RemoteFailed(str(response['status'])+' '+response['name'], res.text)
                else:
                    raise elecmon.exceptions.RemoteFailed('The remote server has encountered an error.', res.text)
        else:
            res.raise_for_status()

    def _query(self, url, data=None):
        self._logger.debug('Getting data from '+str(url)+' ['+str(data)+'].')
        res = self._session.post(url, allow_redirects=False, data=data, stream=True)
        if res.status_code == requests.codes.ok:
            try:
                response = res.json()
            except Exception as e: # for Python3.5 and above, json.decoder.JSONDecodeError will be raised
                raise elecmon.exceptions.RemoteFailed('The remote server has encountered an error.', res.text)

            if 'success' in response and response['success']:
                self._logger.debug('Getting data from '+str(url)+' is successful.')
                return response # success
            else:
                if 'status' in response:
                    raise elecmon.exceptions.RemoteFailed(str(response['status'])+' '+response['name'], res.text)
                else:
                    raise elecmon.exceptions.RemoteFailed('The remote server has encountered an error.', res.text)
        elif res.status_code == requests.codes.found: # 302
            raise elecmon.exceptions.NeedLogin('Need to log in.')
        else:
            res.raise_for_status()
    
    def get_part_list(self):
        part_url = 'https://webapp.bupt.edu.cn/w_dianfei/default/part'
        return self._query(part_url)['data']
    
    def get_floor_list(self, partmentId):
        floor_url = 'https://webapp.bupt.edu.cn/w_dianfei/default/floor'
        return self._query(floor_url, {'partmentId':partmentId})['data']

    def get_drom_list(self, partmentId, floorId):
        drom_url = 'https://webapp.bupt.edu.cn/w_dianfei/default/drom'
        return self._query(drom_url, {'partmentId':partmentId, 'floorId':floorId})['data']

    def get_electricity_data(self, partmentId, floorId, dromNumber):
        search_url = 'https://webapp.bupt.edu.cn/w_dianfei/default/search'
        result = self._query(search_url, {'partmentId':partmentId, 'floorId':floorId, 'dromNumber':dromNumber})['data']
        result['timeRemaining'] = time_remaining(datetime.strptime(result['time'], '%Y-%m-%d %H:%M:%S'), result['pTotal'], float(result['surplus'])+float(result['freeEnd']))
        return result

    def convert_partment(self, dormitory_list):
        partment_list = self.get_part_list()

        for dormitory in dormitory_list:
            drom_found = False
            for partment in partment_list:
                if dormitory['partment'] == partment['partmentName']:
                    dormitory['partment'] = partment['partmentId']
                    drom_found = True
                    break
            if not drom_found:
                raise elecmon.exceptions.PartmentNameNotFound('"'+dormitory['partment']+'" is not in the partment list.')
    
    def query_data(self, dormitory_list):
        self.convert_partment(dormitory_list)

        result = []
        for dormitory in dormitory_list:
            result.append(self.get_electricity_data(dormitory['partment'], dormitory['floor'], dormitory['dormitory']))
        
        return result

    def loop(self, dormitory_list, callback_function, params=None, time_interval=60):
        socket.setdefaulttimeout(time_interval*1.5)

        self._logger.debug('Start getting dormitory list...')

        while True:
            try:
                self.convert_partment(dormitory_list)
                break
            except elecmon.exceptions.RemoteFailed as e:
                self._logger.warning("Can't get dormitory list: %s. Try again after 5 seconds.", str(e))
                self._logger.debug("CONTENTS:\n"+e.content())
                time.sleep(5)

        self._logger.debug('Start collecting datapoints...')

        while True:
            last_exception = None
            start_time = datetime.now()
            for dormitory in dormitory_list:
                attempt = 0
                while attempt < 3:
                    try:
                        attempt += 1
                        callback_function(dormitory, True, 
                            self.get_electricity_data(dormitory['partment'], dormitory['floor'], dormitory['dormitory']), params)
                        break
                    except elecmon.exceptions.LoginFailed as e:
                        last_exception = e
                        self._logger.warning('Login Failed:'+str(e)+' [Attempt: '+str(attempt)+']')
                        self.log_in()
                    except elecmon.exceptions.RemoteFailed as e:
                        last_exception = e
                        self._logger.warning('Remote Server Error:'+str(e)+' [Attempt: '+str(attempt)+']')
                        self._logger.debug('CONTENTS:\n'+e.content())
                    except Exception as e:
                        last_exception = e
                        self._logger.warning(str(e)+' [Attempt: '+str(attempt)+']')
                        self._logger.debug('TRACEBACK:\n', exc_info=True)
                if attempt > 3:
                    callback_function(dormitory, False, {'message': str(last_exception)}, params)
                    self._logger.error('After 3 attempts we still can not get the data, the data points have been skipped. Please wait 60 seconds.')
            end_time = datetime.now()
            fix_interval = (end_time - start_time).total_seconds()
            if fix_interval < time_interval:
                try:
                    time.sleep(time_interval - fix_interval)
                except KeyboardInterrupt:
                    self._logger.info('Aborted by user.')
                    exit()
            else:
                pass # start immediately
            
def time_remaining(time, power, remaining):
    if float(power) == 0:
        return 'Infinite'
    else:
        return (time + timedelta(hours=float(remaining) / float(power))). \
            strftime('%Y-%m-%d %H:%M:%S')
    