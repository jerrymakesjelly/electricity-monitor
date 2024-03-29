# -*- coding:utf-8 -*-
class LoginFailed(Exception):
    def __init__(self, arg):
        Exception.__init__(self, arg)

class NeedLogin(Exception):
    def __init__(self, arg):
        Exception.__init__(self, arg)

class RemoteError(Exception):
    def __init__(self, arg, remote_content = None):
        Exception.__init__(self, arg)

class InvalidDormitoryNumber(Exception):
    def __init__(self, arg):
        Exception.__init__(self, arg)