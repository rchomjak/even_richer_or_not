#!/usr/bin/env python3.6

try:
    import json
    from io import StringIO 
    import decorators
    import jsonschema
    import sys

except ImportError as e:
    print(e, file=sys.stderr)
    exit()

class DataInputHandle(object):
    ''' Take data ,json format, from file and make object from it '''

    SCHEMA = ""

    def __init__(self, input_file_name):

        if not isinstance(input_file_name, str):
            raise TypeError("input_file_name must be string")

        self.input_file_name = input_file_name

    def __open_file(self, input_file_name):
        ''' Open file where data are stored '''
        raise NotImplementedError
            
    def __read_file(self):
        ''' Read file where data are stored.'''
        raise NotImplementedError 

    def check_schema(self):
        raise NotImplementedError

class JsonDataInputHadle(DataInputHandle):

    SCHEMA="asdf"

    def __init__(self, input_file_name):
        DataInputHandle.__init__(input_file_name)
        self.loaded_objects = []

    @__coroutine
    def __check_schema(self, target, check_schema=False):
        ''' Check input data trough Json schema''' 
        input_data = ""
        while True:
            try:
                input_data = (yield)
                if check_schema:
                    jsonschema.Draft4Validator(JsonDataInputHadle.SCHEMA) 
                else:
                    target.send(input_data)

            except jsonschema.ValidationError as e:
                print(e, file=sys.stderr)
                exit()

            except GeneratorExit:
                target.close()

    def __coroutine(self, func):
        ''' decorator functions for coroutines - initialization '''
        def ret_func(*args, **kwargs):
            __func = func(*args, **kwargs)
            next(__func)
            return __func
        return ret_func

    @__coroutine
    def __read_file(self, target):
        try:
            while True:
                fp = (yield)
                target.send(json.loads(fp))
        except GeneratorExit:
            target.close()

    def __open_file(self, target):
        try:
            with open(self.input_file_name, "r") as fp:
                     target.send(fp) 
            target.close()

        except IOError as e:
             print(e, file=sys.stderr)
             exit()
    
    def make_objects(self):
        self.x = [i for i in self.__open_file(self.__read_file(self.__check_schema(self.load_objects)))] 

    def load_objects(self):
        try:
            while True:
                data = (yield)
                self.loaded_objects.insert(data.get('profit_loss', None))

        except GeneratorExit:
            pass

    @classmethod  
    def change_schema(cls, schema):
        
        if not isinstance(schema, str):
            raise TypeError("schema MUST be string.")

        cls.SCHEMA=schema

#TODO Getter/setter    
    def get_objects(self):
        pass
    
    def set_objects(self):
        pass

