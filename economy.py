#!/usr/bin/env python3.6

import copy
import datetime
import dateutil
import re
import sys

from decorators import coroutine


REGULAR, SPECIAL, ALL  = range(0, 3)


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
               
    def __count_sum_loss_profits_costs(self, in_start_date, in_end_date, mode=ALL):
        
        def special(in_start_date, in_end_date):
            costs_special = self.sum_loss_profits.get('costs').get('special',[])
            total_sum = 0
            includes_objects = []
            element_sum = 0
            if len(costs_special):
                for element in costs_special:
                    if in_start_date <= element.get('date') and element.get('date') < in_end_date:
                        element_sum = element.get('value', 0)
                        total_sum = total_sum + element_sum
                        includes_objects.append((element,element_sum))

            return (total_sum, includes_objects)

        def regular(in_start_date, in_end_date):
            costs_regular = self.sum_loss_profits.get('costs').get('regular',[])
            total_sum = 0
            includes_objects = []
            element_sum = 0

            if len(costs_regular):
                for element in costs_regular:
                    value_per_day = element.get('value',0)/ float(element.get('period'))

                    if element.get('start_date') < in_start_date <= element.get('end_date'):
                        element_sum = ((in_start_date - element.get('start_date')).days) * value_per_day
                        includes_objects.append((element, element_sum)) 
                        total_sum = total_sum + element_sum

            return (total_sum, includes_objects)

        if mode == REGULAR:
            return (None, regular(in_start_date, in_end_date))
        elif mode == SPECIAL:
            return (special(in_start_date, in_end_date), None)

    def get_costs(self, in_start_date, in_end_date, mode=ALL):
            return self.__count_sum_loss_profits_costs(in_start_date, in_end_date, mode)

    def __count_sum_loss_profits_return(self, in_start_date, in_end_date, mode=ALL):
        
        def special(in_start_datei, in_end_date):
            returns_special = self.sum_loss_profits.get('returns').get('special',[])
            total_sum = 0
            element_sum = 0
            includes_objects = []

            if len(returns_special):
                for element in returns_special:

                    if in_start_date < element.get('date'):
                        break

                    if  in_start_date <= element.get('date') and element.get('date') < in_end_date:
                        element_sum = element.get('value', 0)
                        total_sum = total_sum + element_sum
                        includes_objects.append((element, element_sum))

            return (total_sum, includes_objects)

        def regular(in_start_date, in_end_date):
            costs_regular = self.sum_loss_profits.get('returns').get('regular',[])
            total_sum = 0
            element_sum = 0
            includes_objects = []

            if len(costs_regular):
                for element in costs_regular:

                    value_per_day = element.get('value', 0)/ float(element.get('period'))

                    if element.get('start_date') < in_start_date <= element.get('end_date'):
                        element_sum =  ((in_start_date - element.get('start_date')).days) * value_per_day
                        total_sum = total_sum + element_sum
                        includes_objects.append((element, total_sum))
            
            return (total_sum, includes_objects)

        if mode == REGULAR:
            return (None, regular(in_start_date, in_end_date))
        elif mode == SPECIAL:
            return (special(in_start_date, in_end_date), None)

    def get_returns(self, in_start_date, in_end_date, mode=ALL):
        return self.__count_sum_loss_profits_return(in_start_date, in_end_date, mode)
       
class CollectionEconomy(object):

    def __init__(self, in_econ_object=[]):

        self.__economy_elements = in_econ_object

    def get_elements(self, ele_type=None, ele_category=None):

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
        def filter_():

            while True:
                in_element = (yield)
                return_elements.append(in_element)
        
        filter_ele_type(filter_ele_category(filter_(), ele_category), ele_type)
        return return_elements 
    
    def get_collection(self,ele_type=None, ele_category=None):
        return CollectionEconomy(self.get_elements(ele_type, ele_category))

    def returns(self, in_start_date, in_end_date, mode=ALL, granulation='YEARLY'):

        def special(in_start_date, in_end_date, mode):

            total_sum = 0
            special_sum = 0

            tmp_eco_element = None

            start_date = in_start_date
            end_date = in_end_date

            tmp_date = None
            tmp_data_element = None
 
            input_objects_dict = {}

            for eco_element in self.__economy_elements:
                tmp_eco_element = eco_element.get_returns(start_date, end_date, mode)
                special_eco_element, regular_eco_element = tmp_eco_element

                if special_eco_element:

                    total_sum = total_sum + special_eco_element[0]

                    for objs in special_eco_element[1]:
                        
                        tmp_date = objs[0].get('date', None)
                        if not tmp_date in input_objects_dict:
                            input_objects_dict[tmp_date]= [[objs[0]], objs[1]]
                        else:
                            tmp_data_element =  input_objects_dict.get(tmp_date)
                            tmp_data_element[1] = tmp_data_element[1] + objs[1]
                            tmp_data_element[0].append(objs[0])

            return (total_sum, input_objects_dict)


        def regular(in_start_date, in_end_date, mode):

            total_sum = 0
            input_objects_dict = {}

            temp_for_date_list_of_data = 0
            tmp_data = None

            start_date = in_start_date
            end_date = in_end_date


            for date in (dateutil.rrule.rrule(getattr(dateutil.rrule, granulation),
                         dtstart=start_date,
                         until=end_date)):

                for eco_element in self.__economy_elements:
                    tmp_eco_element = eco_element.get_returns(date, None, mode)
                    special_eco_element, regular_eco_element = tmp_eco_element
                    

                    if regular_eco_element:
                        total_sum = total_sum + regular_eco_element[0]
                        temp_for_date_list_of_data = regular_eco_element[1]
                        for element in temp_for_date_list_of_data:
                            data, cost = element

                            if date in input_objects_dict:
                                tmp_data = input_objects_dict.get(date)
                                tmp_data[1] = tmp_data[1] + cost
                                tmp_data[0].append(data)

                            else:
                                input_objects_dict[date] = [[data], cost]

            return(total_sum, input_objects_dict)    


        if mode == REGULAR:
            return (regular(in_start_date, in_end_date, mode), None)
        elif mode == SPECIAL:
            return (None, special(in_start_date, in_end_date, mode))
        elif mode == ALL:
            return (regular(in_start_date, in_end_date, mode=REGULAR), special(in_start_date, in_end_date, mode=SPECIAL))

    def costs(self, in_start_date, in_end_date, mode=ALL, granulation='YEARLY'):
        

        def special(in_start_date, in_end_date, mode):

            total_sum = 0
            special_sum = 0

            tmp_eco_element = None

            start_date = in_start_date
            end_date = in_end_date

            tmp_date = None
            tmp_data_element = None
 
            input_objects_dict = {}

            for eco_element in self.__economy_elements:
                tmp_eco_element = eco_element.get_costs(start_date, end_date, mode)
                special_eco_element, regular_eco_element = tmp_eco_element

                if special_eco_element:

                    total_sum = total_sum + special_eco_element[0]

                    for objs in special_eco_element[1]:
                        
                        tmp_date = objs[0].get('date', None)
                        if not tmp_date in input_objects_dict:
                            input_objects_dict[tmp_date]= [[objs[0]], objs[1]]
                        else:
                            tmp_data_element =  input_objects_dict.get(tmp_date)
                            tmp_data_element[1] = tmp_data_element[1] + objs[1]
                            tmp_data_element[0].append(objs[0])

            return (total_sum, input_objects_dict)


        def regular(in_start_date, in_end_date, mode):

            total_sum = 0
            input_objects_dict = {}

            temp_for_date_list_of_data = 0
            tmp_data = None

            start_date = (in_start_date)
            end_date = (in_end_date)


            for date in (dateutil.rrule.rrule(getattr(dateutil.rrule, granulation),
                         dtstart=start_date,
                         until=end_date)):

                for eco_element in self.__economy_elements:
                    tmp_eco_element = eco_element.get_costs(date, None, mode)
                    special_eco_element, regular_eco_element = tmp_eco_element
                    
                    if regular_eco_element:
                        total_sum = total_sum + regular_eco_element[0]
                        temp_for_date_list_of_data = regular_eco_element[1]
                        for element in temp_for_date_list_of_data:
                            data, cost = element

                            if date in input_objects_dict:
                                tmp_data = input_objects_dict.get(date)
                                tmp_data[1] = tmp_data[1] + cost
                                tmp_data[0].append(data)

                            else:
                                input_objects_dict[date] = [[data], cost]

            return(total_sum, input_objects_dict)    


        if mode == REGULAR:
            return (regular(in_start_date, in_end_date, mode), None)
        elif mode == SPECIAL:
            return (None, special(in_start_date, in_end_date, mode))
        elif mode == ALL:
            return ((regular(in_start_date, in_end_date, mode=REGULAR)), (special(in_start_date, in_end_date, mode=SPECIAL)))


    def amortization(self, in_start_date, in_end_date, granulation='YEARLY'):

        total_sum = 0
        
        tmp_amortization_data = None
        tmp_amortization_rate = None

        start_date = (in_start_date)
        end_date = (in_end_date)

        input_objects_dict = {}

        cost = 0
        data = 0

        for date in (dateutil.rrule.rrule(getattr(dateutil.rrule, granulation),
                     dtstart=start_date,
                     until=end_date)):

            for eco_element in self.__economy_elements:
                
                tmp_amortization_data = eco_element.count_amortization_rate(date)
                if tmp_amortization_data is None:
                    continue

                cost, data = tmp_amortization_data

                total_sum = total_sum + cost

                if date in input_objects_dict:
                    tmp_amortization_rate = input_objects_dict.get(date)
                    tmp_amortization_rate[0].extend(data)
                    tmp_amortization_rate[1] += cost 
                    
                else:
                    input_objects_dict[date] = [data, cost]
        return (total_sum, input_objects_dict)


    @property
    def elements(self, in_elements):
        """ Elements are copied """
        self.__economy_elements = copy.deepcopy(in_elements)

        return
    @elements.getter
    def elements(self):
        return self.__economy_elements
       

