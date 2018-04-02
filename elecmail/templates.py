#-*- coding:utf-8 -*-

class TestTemplate(object):
    title = "测试您的 electricity-monitor 邮箱配置"
    content =  'elecmail/templates/testmail.html'

class ReportTemplate(object):
    title = "%s 的用电情况统计报告"
    content = 'elecmail/templates/report.html'

class WarningTemplate(object):
    title = "%s 的剩余电量不足 5 kWh"
    content = 'elecmail/templates/warning.html'