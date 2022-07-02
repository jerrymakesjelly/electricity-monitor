# -*- coding:utf-8 -*-
import sys
import qrcode
import pwinput
import buptelecmon.logger
import buptelecmon.configurationmanager
import buptelecmon.electricitymonitor
import buptelecmon.animateprogress
import buptelecmon.version

# Initialize animate process bar
ap = buptelecmon.animateprogress.AnimateProgress()

# Remaining available time formater
def convert_rat(remaining_hrs):
    return '%dday(s) %.2d:%.2d:%.2d' % (
        remaining_hrs // 24, remaining_hrs % 24,
        remaining_hrs * 60 % 60, remaining_hrs * 3600 % 60
    )

def convert_to_float(v):
    ret = 0
    try:
        ret = float(v)
    except:
        pass
    return ret

def output(data, params=None):
    if data['areaid'] == 1:
        output_xitucheng(data, params)
    else:
        output_shahe(data, params)

# Output formater
def output_xitucheng(data, params=None):
    print('%s %s - Surplus: %.2f kWh (Free: %.2f kWh).' %
        (
            data['dormName'],
            data['time'],
            convert_to_float(data['surplus'])+convert_to_float(data['freeEnd']), convert_to_float(data['freeEnd'])
        )
    )
    print('\t- Voltage/Current/Power/Power Factor: %.1f V, %.3f A, %.1f W, %.2f.' %
        (
            convert_to_float(data['vTotal']),
            convert_to_float(data['iTotal']),
            1000*convert_to_float(data['pTotal']),
            convert_to_float(data['cosTotal'])
        )
    )
    print('\t- Estimated to run out: %s.' %
        (convert_rat((convert_to_float(data['surplus'])+convert_to_float(data['freeEnd'])) / convert_to_float(data['pTotal']))
            if convert_to_float(data['pTotal']) != 0 else 'Infinite')
    )

def output_shahe(data, params=None):
    # Shahe Campus's data format is different from Xitucheng Campus
    print('%s %s - Surplus money: %.2f Yuan\t Total power consumption: %.2f kWh.' %
        (
            data['dormName'],
            data['time'],
            convert_to_float(data['surplus']), convert_to_float(data['freeEnd'])
        )
    )

# Run once mode
def once_mode(username, password, dormitories):
    ap.start_rotated_progress('Pulling data...')
    em = buptelecmon.electricitymonitor.ElectricityMonitor()
    em.login(username, password)
    results = em.query(dormitories)
    ap.stop_progress()
    for dormitory in results:
        output(results[dormitory])

# Run loop mode
def loop_mode(username, password, dormitories):
    print("Electricity Monitor will collect data every 60 seconds.")
    em = buptelecmon.electricitymonitor.ElectricityMonitor()
    em.login(username, password)
    em.loop(dormitories, output)

# Set authorization mode
def set_auth():
    user = input('Student ID: ')
    password = pwinput.pwinput('Password: ')
    return (user, password)

# Recharge mode
def recharge_mode(username, password, dormitory_number):
    em = buptelecmon.electricitymonitor.ElectricityMonitor()
    em.login(username, password)
    qr = qrcode.QRCode()
    qr.add_data(em.get_recharge_link(dormitory_number))
    print('Use your WeChat to scan the QR code of the recharge link.')
    print('Please confirm your information before payment.')
    print()
    qr.print_ascii(invert=True)

# Main function
def main(argv):
    # Create logger
    log = buptelecmon.logger.register(__name__)
    # Create config man
    cman = buptelecmon.configurationmanager.ConfigMan('elecmon', 'elecmon.json')
    try:
        # Set initial parameters
        param = {
            'username': '',
            'password': '',
            'dormitories': []
        }
        # Parse arguments
        if len(argv) > 0 and argv[0] == '--version': # Display version info
            print(buptelecmon.version.about)
        elif len(argv) > 0 and argv[0] == '--set-auth': # Set authorization
            param['username'], param['password'] = set_auth()
            cman.write_back(param)
        else:
            # Load configurations
            param = cman.read()
            # Run
            if len(argv) > 1 and argv[0] == '--recharge': # Recharge mode
                recharge_mode(param['username'], param['password'], argv[1])
            elif len(argv) > 0 and argv[0] == '--loop': # Loop mode
                if len(argv) > 1:
                    param['dormitories'] = argv[1:]
                    cman.write_back(param)
                loop_mode(param['username'], param['password'], param['dormitories'])
            else: # Once mode
                if len(argv) > 0:
                    param['dormitories'] = argv[0:]
                    cman.write_back(param)
                once_mode(param['username'], param['password'], param['dormitories'])
    except KeyboardInterrupt:
        log.info('Aborted by user.')
    except Exception as e:
        ap.stop_progress()
        log.error(str(e))
        log.debug('', exc_info=True)
        log.error("Please check the log for more information.")

# Run by command line
def loader():
    main(sys.argv[1:])

# Run by file name
def init(name):
    if name == '__main__':
        loader()

init(__name__)