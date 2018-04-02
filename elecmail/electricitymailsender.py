#-*- coding:utf-8 -*-
import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr
import codecs
import datetime
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
import logger
from . import templates
import elecrec
from elecrec.dao.datapoint import DataPoint
from elecmon.electricitymonitor import time_remaining

CONSUMPTION_NAME = 'consumption.png'
AVG_POWER_NAME = 'power.png'

class ElectricityMailSender(object):
    def __init__(self, smtp_host, smtp_port, sender, password):
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._sender = sender
        self._password = password

        self._datetime_format = '%a, %d %b %Y %I:%M:%S %p'
        self._date_format = '%a, %d %b %Y'
        self._short_date_format = '%a, %d'
        self._time_format = '%a, %d %b %Y %I:%M:%S %p'

        self._consumption_name = logger.abspath(CONSUMPTION_NAME)
        self._avg_power_name = logger.abspath(AVG_POWER_NAME)

        self._logger = logger.register(__name__)
        self._logger.info('Mail sender was initialized.')

    # Format address
    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    # Format from-address
    def _format_from_addr(self, a):
        return 'BUPT Electricity Monitor <%s>' % a

    # Format to-address
    def _format_to_addr(self, a):
        return '%s <%s>' % (a.split('@')[0], a)

    # Send a mail
    def _send_mail(self, receiver, title, content, attachments=[]):
        # Generate header
        msg = MIMEMultipart()
        msg['From'] = self._format_addr(self._format_from_addr(self._sender))
        for mail in receiver:
            msg['To'] = self._format_addr(self._format_to_addr(mail))
        msg['Subject'] = Header(title, 'utf-8').encode()

        # Content
        msg.attach(MIMEText(content, 'html', 'utf-8'))

        # Attachments
        attach_id = 0
        for attachment in attachments:
            with open(attachment, 'rb') as f:
                mime = MIMEBase('image', 'png', filename=attachment)
                mime.add_header('Content-Disposition', 'attachment', filename=attachment)
                mime.add_header('Content-ID', '<%d>' % attach_id)
                mime.add_header('X-Attachment-Id', '%d' % attach_id)
                mime.set_payload(f.read())
                encoders.encode_base64(mime)
                msg.attach(mime)
                attach_id += 1

        # Send the mail
        server = smtplib.SMTP_SSL(self._smtp_host, self._smtp_port)
        server.ehlo()
        server.login(self._sender, self._password)
        server.sendmail(self._sender, receiver, msg.as_string())
        server.quit()

        self._logger.info('An E-mail was sent to %s.' % (','.join(receiver)))

    # Send a test mail
    def send_test(self, receiver):
        self._send_mail(receiver, templates.TestTemplate.title, 
            codecs.open(logger.abspath(templates.TestTemplate.content), 'r', 'utf-8').read())

    # Draw a bar chart
    def _draw_bar_chart(self, save_path, data, x_labels, y_label, title=''):
        plt.figure(figsize=(10, 6), dpi=80)
        ax1 = plt.subplot(111)
        # Draw bars
        x_bar = range(0, len(data))
        bars = ax1.bar(left=x_bar, height=data, width=0.5, color="lightblue")
        # Add a label for each bar
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x()+0.1, 1.02*height, '%.2f' % height)
        # Set labels
        ax1.set_xticks(x_bar)
        ax1.set_xticklabels(x_labels)
        ax1.set_ylabel(y_label)
        ax1.set_title(title)
        ax1.grid(True)
        plt.savefig(save_path)
        plt.clf()
        plt.close(111)

    # Draw a line chart
    def _draw_line_chart(self, save_path, x_data, y_data, x_label='', y_label='', title=''):
        plt.figure(figsize=(10, 6), dpi=80)
        ax2 = plt.subplot(111)
        # Draw a line
        line = ax2.plot(x_data, y_data, color='orange', marker='o', linestyle='solid')
        # Add a label for each point
        i = 0
        for (x,y) in line[0].get_xydata():
            ax2.text(x-0.5, y+6 if i%2==0 else y-20, '%.2f' % y)
            i+=1
        # Set labels
        ax2.set_xlabel(x_label)
        ax2.set_ylabel(y_label)
        ax2.set_title(title)
        ax2.grid(True)
        plt.savefig(save_path)
        plt.clf()
        plt.close(111)

    # Send the report
    def send_report(self, receivers, dormitory, erec):
        # Get the last datapoint
        last_dp = erec.last_datapoint(dormitory)
        if last_dp == None:
            self._logger.info('No data can be reported.')
            return
        # Get usage of last 7 days
        usage = erec.last_7_days_usage(dormitory)
        # Get average power of last 7 days
        average_power = erec.last_7_days_power(dormitory)
        # Check if the remaining is less than 5 kWh
        title = ''
        notice = ''
        if last_dp.surplus+last_dp.freeEnd < 5:
            remaining = last_dp.surplus+last_dp.freeEnd
            title = templates.WarningTemplate.title % dormitory
            notice = codecs.open(logger.abspath(templates.WarningTemplate.content), 'r', 'utf-8').read() % \
                (remaining, remaining / last_dp.pTotal / 24)
        else:
            title = templates.ReportTemplate.title % dormitory
        # Make parameter structure
        data = {
            'generate_time': datetime.datetime.now().strftime(self._datetime_format),
            'information': notice,
            'dormitory': dormitory,
            'remaining': '%.2f' % (last_dp.surplus+last_dp.freeEnd),
            'freeEnd': '%.2f' % last_dp.freeEnd,
            'vTotal': '%.2f' % last_dp.vTotal,
            'iTotal': '%.2f' % last_dp.iTotal,
            'pTotal': '%.2f' % (1000*last_dp.pTotal),
            'cosTotal': '%.2f' % last_dp.cosTotal,
            'expected_to_use_up': time_remaining(last_dp.time, last_dp.pTotal, 
                last_dp.surplus+last_dp.freeEnd),
            'usage_of_last_7_days': '%.3f' % usage['sum'],
            'max_usage_of_last_7_days': '%.3f' % usage['max']['value'],
            'max_usage_time': usage['max']['date'].strftime(self._date_format),
            'min_usage_of_last_7_days': '%.3f' % usage['min']['value'],
            'min_usage_time': usage['min']['date'].strftime(self._date_format),
            'average_usage_of_last_7_days': '%.2f' % usage['average'],
            'usage_data': [x['value'] for x in usage['data']],
            'usage_date': [x['date'].strftime(self._short_date_format) for x in usage['data']],
            'max_average_power_of_last_7_days': '%.2f' % (1000*average_power['max']['value']),
            'max_power_time': average_power['max']['date'].strftime(self._datetime_format),
            'min_average_power_of_last_7_days': '%.2f' % (1000*average_power['min']['value']),
            'min_power_time': average_power['min']['date'].strftime(self._datetime_format),
            'average_power_of_last_7_days': '%.2f' % (1000*average_power['average']),
            'power_data': [1000*x for x in average_power['data']],
            'power_time': [x for x in range(0, len(average_power['data']))]
        }
        # Draw a bar chart
        self._draw_bar_chart(self._consumption_name, data['usage_data'], data['usage_date'], 'Power Consumption (kWh)',
            'Power Consumption of %s' % data['dormitory'])
        # Draw a line chart
        self._draw_line_chart(self._avg_power_name, data['power_time'], data['power_data'], 'Hour', 'Power (W)',
            'Average Power Per Hour of %s' % data['dormitory'])
        # Generate mail content
        content = codecs.open(logger.abspath(templates.ReportTemplate.content), 'r', 'utf-8').read()
        for x in data:
            content = content.replace('${%s}' % x, str(data[x]))
        # Send the mail
        self._send_mail(receivers, title, content, [self._consumption_name, self._avg_power_name])