# -*- coding:utf-8 -*-
import datetime
import sys
import os
import getopt
import json
import logger
import elecmon
import animateprogress

ap = animateprogress.AnimateProgress()

def output(dormitory, success, data, params=None):
    if success:
        print('%s %s - Remaining: %.2f kWh (Free: %.2f kWh).' 
            % (dormitory['dormitory'], data['time'], float(data['surplus'])+float(data['freeEnd']), float(data['freeEnd'])))
        print('\t- Voltage/Current/Power/Power Factory: %.1f V, %.3f A, %.1f W, %.2f.' 
            % (float(data['vTotal']), float(data['iTotal']), 1000*float(data['pTotal']), float(data['cosTotal'])))
        print('\t- Expected to use up: %s.' % (data['timeRemaining']))
    else:
        print(data['message'])

def daemon_send_report(param, sender, db, threshold):
    for dorm in param['dormitory_list']:
        sender.send_report(dorm['mail_receiver'], dorm['dormitory'], db, threshold)

def daemon_output(dormitory, success, data, params):
    if success:
        # Save into database
        params[0].output(dormitory, success, data)
        # Check if we need to send a mail
        settings = json.load(open(db_config_path, encoding='utf-8'))
        today = datetime.datetime.now().date()
        if (today.strftime('%a') == settings['report_day'] or data['surplus']+data['freeEnd']<settings['warning_threshold'] ) \
            and today.strftime(date_format) != settings['last_report']:
            daemon_send_report(params[2], params[1], params[0], settings['warning_threshold'])
            # Save last report time
            settings['last_report'] = today.strftime(date_format)
            json.dump(settings, open(db_config_path, mode='w', encoding='utf-8'))

def once_mode(param):
    ap.start_rotated_progress('Collecting data...')
    results = elecmon.electricitymonitor.ElectricityMonitor(param['username'], param['password']).query_data(param['dormitory_list'])
    ap.stop_progress()
    for i in range(len(results)):
        output(param['dormitory_list'][i], True, results[i])

def loop_mode(param):
    print("Electricity Monitor collects data every 60 seconds.")
    elecmon.electricitymonitor.ElectricityMonitor(param['username'], param['password']).loop(param['dormitory_list'], output)

def daemon_mode(param, db_param):
    # Initialize database
    er = elecrec.electricityrecorder.ElectricityRecorder(db_param['database'])
    # Initialize mail sender
    sender_param = param['mail_sender']
    em = elecmail.electricitymailsender.ElectricityMailSender(
        sender_param['host'], sender_param['port'],
        sender_param['sender'], sender_param['password']
    )
    elecmon.electricitymonitor.ElectricityMonitor(param['username'], param['password']).loop(param['dormitory_list'],
        daemon_output, params=(er, em, param))

def create_db(db_param):
    elecrec.electricityrecorder.ElectricityRecorder(db_param['database']).create_db()

def send_test_mail(param):
    sender_param = param['mail_sender']
    em = elecmail.electricitymailsender.ElectricityMailSender(
        sender_param['host'], sender_param['port'], 
        sender_param['sender'], sender_param['password']
    )
    for dormitory in param['dormitory_list']:
        em.send_test(dormitory['mail_receiver'])

def send_report_mail(param, db_param):
    sender_param = param['mail_sender']
    em = elecmail.electricitymailsender.ElectricityMailSender(
        sender_param['host'], sender_param['port'], 
        sender_param['sender'], sender_param['password']
    )
    er = elecrec.electricityrecorder.ElectricityRecorder(db_param['database'])
    for dormitory in param['dormitory_list']:
        em.send_report(dormitory['mail_receiver'], dormitory['dormitory'], er)

if __name__ == '__main__':
    # Modes
    ONCE = 1
    LOOP = 2
    DAEMON = 3
    CREATE_DB = 4
    SEND_TEST_MAIL = 5
    SEND_REPORT = 6
    # configurations
    mode = ONCE
    import_elecrec = False
    import_elecmail = False
    file_path = logger.abspath('elecmon.json')
    date_format = '%Y-%m-%d'
    db_config_path = logger.abspath('daemon.json')
    db_config = {
        'database': './database/record.db',
        'report_day': 'Sat',
        'warning_threshold': 5,
        'last_report': datetime.datetime.now().date().strftime(date_format)
    }

    # Create logger
    log = logger.register(__name__)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:ld", ["config=", "loop", "daemon", "create-database", "send-test-mail", "send-report"])
    except getopt.GetoptError:
        log.error('Invalid arguments.')
        exit(0)
    
    for opt, arg in opts:
        if opt in ("-c", "--config"):
            file_path = arg
        elif opt in ("-l", "--loop"):
            mode = LOOP
        elif opt in ("-d", "--daemon"):
            import_elecmail = import_elecrec = True
            mode = DAEMON
        elif opt == "--create-database":
            import_elecrec = True
            mode = CREATE_DB
        elif opt == '--send-test-mail':
            import_elecmail = True
            mode = SEND_TEST_MAIL
        elif opt == '--send-report':
            import_elecmail = import_elecrec = True
            mode = SEND_REPORT

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            param = json.load(f)
        
        # Load database configurations
        if import_elecrec:
            if os.path.exists(db_config_path):
                with open(db_config_path, 'r', encoding='utf-8') as f:
                    db_config = json.load(f)
            else:
                with open(db_config_path, 'w', encoding='utf-8') as f:
                    json.dump(db_config, f)
        
        # Load modules
        if import_elecmail:
            import elecmail
        if import_elecrec:
            import elecrec

        if mode == ONCE:
            once_mode(param)
        elif mode == LOOP:
            loop_mode(param)
        elif mode == DAEMON:
            daemon_mode(param, db_config)
        elif mode == CREATE_DB:
            create_db(db_config)
        elif mode == SEND_TEST_MAIL:
            send_test_mail(param)
        elif mode == SEND_REPORT:
            send_report_mail(param, db_config)
    except Exception as e:
        ap.stop_progress()
        log.error("Can't initialize: "+str(e))
        log.debug("Traceback for debug:\n", exc_info=True)
        log.error("Please check the log for more information.")
