#!/usr/bin/env python3.6

import copy
import datetime
import re
import sys

from decorators import coroutine


class Economy(object):
    """ The object will be filled with variables from input to __dict__ """
    def __init__(self):
        self.__after_amortization_value = 0
        self.__difference_prob_amor_rate_val_realize_val = 0
        self.__prob_realize_value = 0 


    def __after_data_load(self):
        #amortization rate MUST be sorted by date
        self.value.get('amortization_rate', []).sort(key=lambda x: x.date)
        self.sum_loss_profits.get('costs').get('special',[]).sort(key=lambda x: x.date)
        self.sum_loss_profits.get('return').get('special',[]).sort(key=lambda x: x.date)



    def count_amortization_rate(self, in_date):
        """ Counting amortization rate as exponencial function value*(rate**diff_days) """

        total_sum = 0
        def pairs(i):
            it = iter(i)
            while True:
                try:
                    yield(next(it))
            
                except StopIteration:
                    yield ({"date":datetime.datetime.max})
                    break


        if len(self.value) and len(self.value.get('amortization_rate', [])):

            if in_date < self.operation.get('date_acquire'):
                print("input is before than date of acquire", file=sys.stderr)
                total_sum = 0
            elif in_date == self.operation.get('date_acquire'):
                total_sum = self.value.get('acquire_value')
                
            else:

                total_sum = self.value.get('acquire_value')
                amor_rate = list(pairs(self.value.get('amortization_rate', [])))
                amor_rate_1 = amor_rate.pop(0)
                amor_rate_2 = amor_rate.pop(0)
                includes_objects = [amor_rate_1]

                try:
                    if in_date < amor_rate_1.get('date'):
                        self.__prob_realize_value = total_sum
                        return (total_sum, [])
                        

                    while (in_date > amor_rate_2.get('date')):
                        includes_objects.append(amor_rate_2)
                        total_sum = total_sum * ((amor_rate_1.get('value')**(1/float(amor_rate_1.get('period'))))**((amor_rate_2.get('date') - amor_rate_1.get('date')).days))
                        amor_rate_1 = amor_rate_2
                        amor_rate_2 = amor_rate.pop(0)

                    if in_date <= amor_rate_2.get('date'):
                        total_sum = total_sum * ((amor_rate_1.get('value')**(1/float(amor_rate_1.get('period'))))**(in_date - amor_rate_1.get('date')).days)
                        includes_objects.append(amor_rate_2)

                    
                except IndexError:
                    pass
                                 
                
                self.__prob_realize_value = total_sum
                return (total_sum, includes_objects)
               
    def __count_sum_loss_profits_costs(self, in_date, mode="all"):
        
        def special(in_date):
            costs_special = self.sum_loss_profits.get('costs').get('special',[])
            total_sum = 0
            includes_objects = []
            element_sum = 0

            if len(costs_special):
                for element in costs_special:
                    if in_date < element.get('date'):
                        break

                    if in_date >= element.get('date'):
                        element_sum = element.get('value', 0)
                        total_sum = total_sum + element_sum
                        includes_objects.append({element:element_sum})

            return (total_sum, includes_objects)

        def regular(in_date):
            costs_regular = self.sum_loss_profits.get('costs').get('regular',[])
            total_sum = 0
            includes_objects = []
            element_sum = 0

            if len(costs_regular):
                for element in costs_regular:
                    value_per_day = element.get('value',0)/ float(element.get('period'))

                    if element.get('start_date') < in_date <= element.get('end_date'):
                        element_sum = ((in_date - element.get('start_date')).days) * value_per_day
                        includes_object.append({element:element_sum}) 
                        total_sum = total_sum + element_sum

                return (total_sum, includes_object)

        if mode == "all":
            return (special(in_date), regular(in_date))
        elif mode == "regular":
            return (None, regular(in_date))
        elif mode == "special":
            return (special(in_date), None)

    def get_costs(self, in_date, mode="all"):
            return self.__count_sum_loss_profits_costs(in_date, mode)

    @property
    def costs(self, value):
        raise AttributeError("You cannot change this attribute.")

    def __count_sum_loss_profits_return(self, in_date, mode="all"):
        
        def special(in_date):
            costs_special = self.sum_loss_profits.get('returns').get('special',[])
            total_sum = 0
            element_sum = 0
            includes_objects = []

            if len(costs_special):
                for element in costs_special:

                    if in_date < element.get('date'):
                        break

                    if in_date >= element.get('date'):
                        element_sum = element.get('value', 0)
                        total_sum = total_sum + element_sum
                        includes_objects.append({element:element_sum})


            return (total_sum, includes_objects)

        def regular(in_date):
            costs_regular = self.sum_loss_profits.get('costs').get('returns',[])
            total_sum = 0
            element_sum = 0
            includes_objects = []

            if len(costs_regular):
                for element in costs_regular:

                    value_per_day = element.get('value', 0)/ float(element.get('period'))

                    if element.get('start_date') < in_date <= element.get('end_date'):
                        element_sum =  ((in_date - element.get('start_date')).days) * value_per_day
                        total_sum = total_sum + element_sum
                        includes_objects.append({element:total_sum})
            
                return (total_sum, includes_objects)

        if mode == "all":
            return (special(in_date), regular(in_date))
        elif mode == "regular":
            return (None, regular(in_date))
        elif mode == "special":
            return (special(in_date), None)

    def get_returns(self, in_date, mode="all"):
        return self.__count_sum_loss_profits_return(in_date, mode)

    @property
    def returns(self, value):
        raise AttributeError("You cannot change this attribute.")

       
class CollectionEconomy(object):
    def __init__(self, in_econ_object=[]):

        self.__economy_elements = in_econ_object

    def get_elements(self, ele_type=None, ele_category=None, ele_global_event=False):

        return_elements = []

        def filter_ele_type(target, ele_type):
            for element in self.__economy_elements:
                if element.type == ele_type or ele_type is None:
                    target.send(element)
            target.close()     

        @coroutine
        def filter_ele_category(target, ele_category):
            
            while True:

                in_element = (yield)
                if in_element.category == ele_category or (ele_category is None):
                    target.send(in_element)
            target.close()

        @coroutine
        def filter_ele_global_type(ele_global_event):

            while True:
                in_element = (yield)
                if (ele_global_event is None) or (in_element.global_event == ele_global_event):
                    return_elements.append(in_element)
        
        filter_ele_type(filter_ele_category(filter_ele_global_type(ele_global_event), ele_category), ele_type)
        return return_elements 

    def get_collection(self,ele_type=None, ele_category=None, ele_global_event=False):
       pass 

    @property
    def elements(self, in_elements):
        """ Elements are copied """
        self.__economy_elements = copy.deepcopy(in_elements)

        return
       

