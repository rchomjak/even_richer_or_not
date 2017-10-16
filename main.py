#!/usr/bin/env python3
import jsonoperation
import economy
import matplotlib.pylab as plt
import datetime
import dateutil
import collections
import dateutil.rrule as daterr

a = jsonoperation.JsonDataInputHadle(["input.json"])
a.make_objects()


cole = a.collection_economy_objects

start_date = "2016 10 5"
end_date = "2017 12 5"

print(cole.costs(start_date, end_date, mode=economy.REGULAR))

CostsReturns = collections.namedtuple('CostsReturns', ['total_sum', 'special_sum', 'regular_sum', 'rest'])

x_line = [datetime.datetime(2013, 10, 5, 0, 0),datetime.datetime(2017, 10, 5, 0, 0), datetime.datetime(2017, 10, 1, 0, 0), datetime.datetime(2020,1,1,0,0) ]
y_total_line = [0,250, 500,0]
y_regular_sum = [0, 250, 750,]
y_special_sum = [1,2,4,5,5]

#plt.hist(y_total_line,4, cumulative=True)

'''
plt.plot([1,2,3,4], y_total_line, label='test')
#plt.plot(x_line, y_regular_sum, label='test2')
plt.plot([10,20,30,40,50], y_special_sum, label='test3')
plt.legend()
plt.show()
'''
