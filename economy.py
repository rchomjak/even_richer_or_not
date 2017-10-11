#!/usr/bin/env python3.6


import datetime
import re
import sys

class Economy(object):
    """ The object will be filled with variables from input. """
    def __init__(self):
        self.__after_amortization_value = 0
        self.__difference_prob_amor_rate_val_realize_val = 0
        self.__prob_realize_value = 0 


    def __after_data_load(self):
        #amortization rate MUST be sorted by date
    #TODO check if data has been changed
        self.value.get('amortization_rate', []).sort(key=lambda x: x.date)


    #should insert a date
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
 
                try:
                    if in_date < amor_rate_1.get('date'):
                        self.__prob_realize_value = total_sum
                        return self.__prob_realize_value
                        

                    while (in_date > amor_rate_2.get('date')):
                        total_sum = total_sum * ((amor_rate_1.get('value')**(1/float(amor_rate_1.get('period'))))**((amor_rate_2.get('date') - amor_rate_1.get('date')).days))
                        amor_rate_1 = amor_rate_2
                        amor_rate_2 = amor_rate.pop(0)

                    if in_date <= amor_rate_2.get('date'):
                        total_sum = total_sum * ((amor_rate_1.get('value')**(1/float(amor_rate_1.get('period'))))**(in_date - amor_rate_1.get('date')).days)
                    
                except IndexError:
                    pass
                                 
                
                self.__prob_realize_value = total_sum
                return self.__prob_realize_value
               


