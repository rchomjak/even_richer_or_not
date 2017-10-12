#!/usr/bin/env python3.5
import jsonoperation
import economy

    
a = jsonoperation.JsonDataInputHadle(["input.json"])
a.make_objects()

import datetime

print (a.economy_objects[0].count_amortization_rate(datetime.datetime.strptime("2015 8 5", "%Y %m %d")))



cole = economy.CollectionEconomy(a.economy_objects)
elements = cole.get_elements()


