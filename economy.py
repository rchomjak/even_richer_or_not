#!/usr/bin/env python3.6

import copy
import datetime
import dateutil
import re
import sys

from decorators import coroutine


REGULAR, SPECIAL, ALL = range(0, 3)


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

        if mode == ALL:
            return (special(in_start_date, in_end_date), regular(in_start_date, in_end_date))
        elif mode == REGULAR:
            return (None, regular(in_start_date, in_end_date))
        elif mode == SPECIAL:
            return (special(in_start_date, in_end_date), None)

    def get_costs(self, in_start_date, in_end_date, mode=ALL):
            return self.__count_sum_loss_profits_costs(in_start_date, in_end_date, mode)

    def __count_sum_loss_profits_return(self, in_date, mode=ALL):
        
        def special(in_date):
            returns_special = self.sum_loss_profits.get('returns').get('special',[])
            total_sum = 0
            element_sum = 0
            includes_objects = []

            if len(returns_special):
                for element in returns_special:

                    if in_date < element.get('date'):
                        break

                    if in_date >= element.get('date'):
                        element_sum = element.get('value', 0)
                        total_sum = total_sum + element_sum
                        includes_objects.append((element, element_sum))


            return (total_sum, includes_objects)

        def regular(in_date):
            costs_regular = self.sum_loss_profits.get('returns').get('regular',[])
            total_sum = 0
            element_sum = 0
            includes_objects = []

            if len(costs_regular):
                for element in costs_regular:

                    value_per_day = element.get('value', 0)/ float(element.get('period'))

                    if element.get('start_date') < in_date <= element.get('end_date'):
                        element_sum =  ((in_date - element.get('start_date')).days) * value_per_day
                        total_sum = total_sum + element_sum
                        includes_objects.append((element, total_sum))
            
            return (total_sum, includes_objects)

        if mode == ALL:
            return (special(in_date), regular(in_date))
        elif mode == REGULAR:
            return (None, regular(in_date))
        elif mode == SPECIAL:
            return (special(in_date), None)

    def get_returns(self, in_date, mode=ALL):
        return self.__count_sum_loss_profits_return(in_date, mode)
       
class CollectionEconomy(object):

    #Granularity
    DAY, MONTH, YEAR = range(0, 3)

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
        return CollectionEconomy(self.get_elements(ele_type, ele_category, ele_global_event))

    def returns(self, in_start_date, in_end_date, mode=ALL):
        returns_objects = []
        special_objects = []
        empty_objects = []

        total_sum = 0
        regular_sum = 0
        special_sum = 0

        tmp_eco_element = None

        for date in (dateutil.rrule.rrule(dateutil.rrule.MONTHLY,
                     dtstart=dateutil.parser.parse(in_start_date),
                     until=dateutil.parser.parse(in_end_date))):

            for eco_element in self.__economy_elements:
                tmp_eco_element = eco_element.get_returns(date, mode)
                special_eco_element, regular_eco_element = tmp_eco_element

                if special_eco_element:
                    if not special_eco_element[1] not in special_objects:
                        total_sum = total_sum + special_eco_element[0]
                        special_sum = special_sum + special_eco_element[0]
                        special_objects.append(special_eco_element[1])
                        returns_objects.append(tmp_eco_element)

                    elif not date in empty_objects:
                        empty_objects.append(date)
                        returns_objects.append({date:(0,[])})
                
                if regular_eco_element:
                    total_sum = total_sum + regular_eco_element[0]
                    regular_sum = regular_sum + regular_eco_element[0]
                    returns_objects.append(tmp_eco_element)



        assert round(total_sum, 3) == (round(regular_sum, 3) + round(special_sum, 3)), "Total sum does not equal the subsums"
        return (total_sum, special_sum, regular_sum, returns_objects)

    def costs(self, in_start_date, in_end_date, mode=ALL):
        

        def special(in_start_date, in_end_date, mode):

            total_sum = 0
            special_sum = 0
            regular_sum = 0

            tmp_eco_element = None

            start_date = dateutil.parser.parse(in_start_date)
            end_date = dateutil.parser.parse(in_end_date)

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

            print(total_sum, special_sum, input_objects_dict)
            return (total_sum, special_sum, regular_sum, input_objects_dict)

        #return special(in_start_date, in_end_date, mode)

        def regular(in_start_date, in_end_date, mode):

            special_eco_element = None
            regular_sum = 0
            total_sum = 0
            costs_objects = []
            input_objects_dict = {}

            temp_for_date_total_cost = 0
            temp_for_date_list_of_data = 0
            tmp_data = None

            start_date = dateutil.parser.parse(in_start_date)
            end_date = dateutil.parser.parse(in_end_date)


            for date in (dateutil.rrule.rrule(dateutil.rrule.MONTHLY,
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



                          #  objs, cost
                            #print(regular_eco_element)
                        #tmp_data_element = ip
                    #    regular_sum = regular_sum + regular_eco_element[0]
                    #    total_sum = total_sum + regular_eco_element[0]            
                    #    costs_objects.append({date:tmp_eco_element})

                    #costs_objects.append({date:copy.deepcopy(input_objects)})
                    #input_objects.clear()
            print(input_objects_dict)
            return(total_sum, regular_sum, costs_objects)    
        print("pokemon")
        return regular(in_start_date, in_end_date, mode)
       #print(total_sum, regular_sum, special_sum)
       #assert round(total_sum, 3) == (round(regular_sum, 3) + round(special_sum, 3)), "Total sum does not equal the subsums"

    @property
    def elements(self, in_elements):
        """ Elements are copied """
        self.__economy_elements = copy.deepcopy(in_elements)

        return
       

