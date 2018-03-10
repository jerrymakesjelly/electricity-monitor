# -*- coding:utf-8 -*-
class LoginFailed(Exception):
    def __init__(self, arg):
        Exception.__init__(self, arg)

class NeedLogin(Exception):
    def __init__(self, arg):
        Exception.__init__(self, arg)

class RemoteFailed(Exception):
    def __init__(self, arg, remote_content):
        Exception.__init__(self, arg)
        self._remote_content = remote_content
    
    def content(self):
        return self._remote_content

class PartmentNameNotFound(Exception):
    def __init__(self, arg):
        Exception.__init__(self, arg)