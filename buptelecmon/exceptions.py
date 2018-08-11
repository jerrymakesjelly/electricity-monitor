# -*- coding:utf-8 -*-
class LoginFailed(Exception):
    def __init__(self, arg):
        Exception.__init__(self, arg)

class NeedLogin(Exception):
    def __init__(self, arg):
        Exception.__init__(self, arg)

class RemoteError(Exception):
    def __init__(self, arg, remote_content):
        Exception.__init__(self, arg)

class PartmentNameNotFound(Exception):
    def __init__(self, arg):
        Exception.__init__(self, arg)

class InvalidDormitoryNumber(Exception):
    def __init__(self, arg):
        Exception.__init__(self, arg)