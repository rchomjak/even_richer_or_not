#!/usr/bin/env python3.6


import json
import jsonschema
import sys

import economy
from decorators import coroutine


class DataInputHandle(object):
    """ Take data from file and make object from it """

    SCHEMA = ""

    def __init__(self, input_file_name):

        self.input_file_name = input_file_name

    def __open_file(self, input_file_name):
        """ Open file where data are stored. """
        raise NotImplementedError
            
    def __read_file(self):
        """ Read file where data are stored."""
        raise NotImplementedError 

    def __check_schema(self):
        raise NotImplementedError

class JsonDataInputHadle(DataInputHandle):

    SCHEMA="asdf"

    def __init__(self, input_file_name="", loaded_objects = []):
        DataInputHandle.__init__(self, input_file_name)
 
        self.is_extern_load_object = False 
        self.loaded_objects = loaded_objects       

        if not len(self.input_file_name) and self.loaded_objects is None:
            raise TypeError("Invalid parameters.")

        if isinstance(loaded_objects, dict) and len(loaded_objects):
            self.is_extern_load_object = True

        self.__economy_objects = []

    @coroutine
    def __check_schema(self, target, check_schema=False):
        """ Check input data trough JSON schema"""
        input_data = ""
        while True:
                input_data = (yield)
                if check_schema:
                    jsonschema.Draft4Validator(JsonDataInputHadle.SCHEMA) 
                else:
                    target.send(input_data)

    @coroutine
    def __read_file(self, target):
            while True:
                fp = (yield)
                target.send(json.loads(fp.read()))
            

    def __open_file(self, target):
            with open(self.input_file_name, "r") as fp:
                     target.send(fp) 
            target.close()

    
    def make_objects(self):
        """ makes pipe from file: open_file | read_file | load_object > self.loaded_object """
        #create pipeline which fill self.loaded_objects
        if not self.is_extern_load_object:
            self.__open_file(self.__read_file(self.__check_schema(self.__load_objects()))) 

        for in_var in self.loaded_objects:
            tmp_econ = economy.Economy()
            tmp_econ.__dict__ = in_var
            self.__economy_objects.append(tmp_econ)

    @coroutine
    def __load_objects(self):
            while True:
                data = (yield)
                for obj in data.get('profit_loss', []):
                    self.loaded_objects.append(obj)


    @classmethod  
    def change_schema(cls, schema):
        
        if not isinstance(schema, str):
            raise TypeError("schema MUST be string.")

        cls.SCHEMA=schema

    @property
    def economy_objects(self, value):
        raise AttributeError("You cannot change this value")

    @economy_objects.getter 
    def economy_objects(self):
        return self.__economy_objects
   
    @property
    def extern_status(self):
        return self.is_extern_load_object

    @extern_status.setter
    def extern_status(self, status):
        if not isinstance(status, bool):
            raise TypeError("Invalid parameters")
        self.is_extern_load_object = status

    @property
    def raw_objects(self):
        return self.loaded_objects

    @raw_objects.setter
    def raw_objects(self, loaded_objects):
        self.loaded_objects = loaded_objects
        self.is_extern_load_object = True


