# -*- coding:utf-8 -*-
import sys
import getopt
import json
import logger
import elecmon

def main(argv):
    # Modes
    ONCE = 1
    LOOP = 2
    # configurations
    mode = ONCE
    file_path = 'elecmon.json'

    try:
        opts, args = getopt.getopt(argv, "c:ld", ["config=", "loop", "daemon"])
    except getopt.GetoptError:
        pass
    
    for opt, arg in opts:
        if opt in ("-c", "--config"):
            file_path = arg
        elif opt in ("-l", "--loop"):
            mode = LOOP

    # Create logger
    log = logger.register(__name__)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            param = json.load(f)

        if mode == ONCE:
            once_mode(param)
        elif mode == LOOP:
            loop_mode(param)
    except Exception as e:
        log.error("Can't initialize: "+str(e))
        log.debug("Traceback for debug:\n", exc_info=True)
        log.error("Please check the log for more information.")

def output(dromitory, success, data):
    if success:
        print('%s %s - Power remaining: %.2f kWh (Free: %.2f kWh).' 
            % (dromitory['dromitory'], data['time'], float(data['surplus'])+float(data['freeEnd']), float(data['freeEnd'])))
        print('\t- Voltage/Current/Power/Power Factory: %.1f V, %.3f A, %.3f kW, %.2f.' 
            % (float(data['vTotal']), float(data['iTotal']), float(data['pTotal']), float(data['cosTotal'])))
        print('\t- Time Remaining: %s.' % (data['timeRemaining']))
    else:
        print(data['message'])

def once_mode(param):
    results = elecmon.electricitymonitor.ElectricityMonitor(param['username'], param['password']).query_data(param['dromitory_list'])
    for i in range(len(results)):
        output(param['dromitory_list'][i], True, results[i])

def loop_mode(param):
    print("Electricity Monitor collects data every 60 seconds.")
    elecmon.electricitymonitor.ElectricityMonitor(param['username'], param['password']).loop(param['dromitory_list'], output)

if __name__ == '__main__':
    main(sys.argv[1:])