#-*- coding:utf-8 -*-
import logger
import datetime
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .dao.datapoint import DataPoint

class ElectricityRecorder(object):
    def __init__(self, path):
        self._engine = create_engine('sqlite:///'+logger.abspath(path))
        self._dbsession = sessionmaker(bind=self._engine)

        self._logger = logger.register(__name__)
        self._logger.info('Database initialized.')

    # Create database
    def create_db(self):
        DataPoint.metadata.create_all(self._engine)

    # Put data points into database
    def output(self, dormitory, success, data):
        if success:
            t = datetime.datetime.strptime(data['time'], '%Y-%m-%d %H:%M:%S')
            dp = DataPoint(dormitoryName = dormitory['dormitory'], 
                time = t, hour = t.hour,
                phone = data['phone'], model = data['model'],
                vTotal = data['vTotal'], price = data['price'],
                iTotal = data['iTotal'], freeEnd = data['freeEnd'],
                cosTotal = data['cosTotal'], pTotal = data['pTotal'],
                surplus = data['surplus'], totalActiveDisp = data['totalActiveDisp'])
            session = self._dbsession()
            session.add(dp)
            session.commit()
            session.close()
            self._logger.info('Collected data point: Remaining of %s: %f kWh.', 
                dormitory['dormitory'], data['freeEnd']+data['surplus'])
        else:
            self._logger.error('Lost data point: %s. Reason: %s.', dormitory['dormitory'], data['message'])
    
    # Get the last data point
    def last_datapoint(self, dormitory):
        return self._dbsession().query(DataPoint).filter(DataPoint.dormitoryName==dormitory) \
            .order_by(desc(DataPoint.time)).first()
    
    def last_7_days_usage(self, dormitory):
        session = self._dbsession()
        result = {
            'min': {'value': None, 'date': ''},
            'max': {'value': None, 'date': ''},
            'sum': 0,
            'average': 0,
            'data': []
        }
        # Get the usage of the last 7 days
        end_date = datetime.datetime.now().date()
        current_date = end_date - datetime.timedelta(days=7)
        while current_date < end_date:
            dp_filter = session.query(DataPoint).filter(DataPoint.dormitoryName==dormitory) \
                .filter(DataPoint.time.between(current_date, current_date+datetime.timedelta(days=1)))
            # the first data point
            first_dp = dp_filter.first()
            first_disp = first_dp.totalActiveDisp if first_dp != None else 0
            # the last data point
            last_dp = dp_filter.order_by(desc(DataPoint.time)).first()
            last_disp = last_dp.totalActiveDisp if last_dp != None else 0
            # usage
            usage = last_disp - first_disp
            if result['max']['value'] == None or usage > result['max']['value']:
                result['max']['value'] = usage
                result['max']['date'] = current_date
            if result['min']['value'] == None or usage < result['min']['value']:
                result['min']['value'] = usage
                result['min']['date'] = current_date
            result['sum'] += usage
            result['data'].append({'value':usage, 'date':current_date})
            
            current_date += datetime.timedelta(days=1)
        result['average'] = result['sum'] / 7
        return result
    
    def last_7_days_power(self, dormitory):
        session = self._dbsession()
        result = {
            'min': {'value': None, 'date': ''},
            'max': {'value': None, 'date': ''},
            'average': 0,
            'data': [0 for i in range(0,24)]
        }
        # Get the power of the last 7 days
        first_dp_of_7_days = None
        last_dp_of_7_days = None
        for hour in range(0, 24):
            end_date = datetime.datetime.now().date()
            current_date = end_date - datetime.timedelta(days=7)
            count = 0
            while current_date < end_date:
                dps = session.query(DataPoint).filter(DataPoint.dormitoryName==dormitory) \
                    .filter(DataPoint.time.between(current_date, current_date+datetime.timedelta(days=1))) \
                    .filter(DataPoint.hour==hour) \
                    .all()
                # the first and the last data point
                first_dp = None
                last_dp = None
                for dp in dps:
                    # First data point
                    if first_dp == None:
                        first_dp = dp
                    if first_dp_of_7_days == None:
                        first_dp_of_7_days = dp
                    # Last data point
                    last_dp = dp
                    last_dp_of_7_days = dp
                    # Maximum
                    if result['max']['value'] == None or dp.pTotal > result['max']['value']:
                        result['max']['value'] = dp.pTotal
                        result['max']['date'] = dp.time
                    # Minimum
                    if result['min']['value'] == None or dp.pTotal < result['min']['value']:
                        result['min']['value'] = dp.pTotal
                        result['min']['date'] = dp.time
                if first_dp != None and last_dp != None and (last_dp.time-first_dp.time).seconds != 0:
                    result['data'][hour] += (last_dp.totalActiveDisp-first_dp.totalActiveDisp) / \
                        ((last_dp.time-first_dp.time).total_seconds()/3600)
                    count+=1
                current_date += datetime.timedelta(days=1)
            if count != 0:
                result['data'][hour] /= count
        # Get average
        if first_dp_of_7_days != None and last_dp_of_7_days != None:
            result['average'] = \
                (last_dp_of_7_days.totalActiveDisp - first_dp_of_7_days.totalActiveDisp) / \
                ((last_dp_of_7_days.time - first_dp_of_7_days.time).total_seconds() / 3600)
        # Fix zeroes
        if result['max']['value'] == None:
            result['max']['value'] = 0
            result['max']['date'] = current_date
        if result['min']['value'] == None:
            result['min']['value'] = 0
            result['min']['date'] = current_date
        
        return result