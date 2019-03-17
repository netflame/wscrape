# -*- coding: utf-8 -*-

class DataError(Exception):
    def __init__(self, err_msg):
        super().__init__(self)
        self.err_msg = err_msg
    
    def __str__(self):
        return self.err_msg
    
    def __repr__(self):
        return self.__str__()