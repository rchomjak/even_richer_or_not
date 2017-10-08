#!/usr/bin/env python3.6

try:
    import json
    import jsonschema
    import sys

#project files
    import economy


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

    def __init__(self, input_file_name="", loaded_objects = None):
        DataInputHandle.__init__(input_file_name)
 
        self.is_extern_load_object = False 
        self.loaded_objects = loaded_objects       

        if not len(self.input_file_name) and self.loaded_objects is None:
            raise TypeError("Invalid parameters.")

        if isinstance(loaded_objects, None):
            self.is_extern_load_object = True

        self.__economy_objects = []

    def __coroutine(self, func):
        ''' decorator functions for coroutines - initialization '''
        def ret_func(*args, **kwargs):
            __func = func(*args, **kwargs)
            next(__func)
            return __func
        return ret_func

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
        ''' makes pipe from file: open_file | read_file | load_object > self.loaded_object '''
        #create pipeline which fill self.loaded_objects
        if not self.is_extern_load_object:
            self.__open_file(self.__read_file(self.__check_schema(self.__load_objects))) 

        for in_var in self.loaded_objects:
            tmp_econ = economy.Economy()
            tmp_econ.__dict__ = in_var
            self.__economy_objects.insert(tmp_econ)


    def __load_objects(self):
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

    @economy_objects.setter
    def economy_objects(self):
        return self.__economy_objects
   
    @economy_objects.getter
    def economy_objects(self, value):
        raise AttributeError("You cannot change this value")

    @extern_status.getter 
    def extern_status(self):
        return self.is_extern_load_object

    @extern_status.setter
    def extern_status(self, status):
        if not isinstance(status, bool):
            raise TypeError("Invalid parameters")
        self.is_extern_loaded_object = status

    @raw_objects.getter
    def raw_objects(self):
        return self.loaded_objects

    @raw_objects.setter
    def raw_objects(self, loaded_objects):
        self.loaded_objects = loaded_objects
        self.is_extern_load_object = True


