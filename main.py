#!/usr/bin/env python3

try:
    import argparse
    import base64
    import collections
    import io
    import sys

    import jsonoperation
    import matplotlib.pylab as plt


except (ImportError, ModuleNotFoundError) as e:
    print(e, file=sys.stderr)
    dependencies = "Dependencies: Matplotlib + pylab, dateutil"
    print(dependencies, file=sys.stderr)




def check_date(input_string):

    import re
    import dateutil.parser

    re_date_str = '(?P<DATE>(?P<YEAR>\d\d\d\d)([-| ])?(?P<MONTH>\d{1,2})?([-| ])?(?P<DAY>\d{,2}))'
    matched_date = re.match(re_date_str, input_string)
    
    if not matched_date:
        raise argparse.ArgumentTypeError("Input string: {0} is not valid date format".format(input_string))
    return dateutil.parser.parse(input_string)
    


parser = argparse.ArgumentParser(description="Program counts and plots some economical data to HTML file as SVG files.")
parser.add_argument('--input-file', action='append', help="Data file in JSON format", required=True)
parser.add_argument('--output-file', action='store', help="Name of output in HTML format", required=True)
parser.add_argument('--start-date', type=check_date, help="Start date of range in format YYYY MM DD", required=True)
parser.add_argument('--end-date', type=check_date, help="End date of range in format YYYY MM DD", required=True)
parser.add_argument('--filter-type', action='store', help="Data are filtered based on type in JSON data file. Case sensitive. Default: None", default=None)
parser.add_argument('--filter-category', action='store', help="Data are filtered based on category in JSON data file. Case sensitive. Default: None", default=None)
parser.add_argument('--granularity', action='store', type=str, help="Sets granularity for generating a date range - size of step. Default: YEARLY", choices=['DAILY, MONTHLY, YEARLY'], default='YEARLY')

#pridat example



DateDataCollection = collections.namedtuple('DateDataCollecion', ['start_date', 'end_date', 'granularity', 'collection'])

AmortizationCollection = collections.namedtuple('Amortization', ['total_cost', 'date_value'])

ReturnsCostsCollection = collections.namedtuple('ReturnsCosts', ['regular', 'special'])

def make_data(parsed_data):
    
    start_date = parsed_data.start_date
    end_date = parsed_data.end_date
    input_files = parsed_data.input_file

    ele_type = parsed_data.filter_type
    ele_category = parsed_data.filter_category
    
    granularity = parsed_data.granularity

    #Loads JSON files and makes economy object 
    data = jsonoperation.JsonDataInputHadle(input_files)
    data.make_objects()

    e_collection = data.collection_economy_objects
    filtered_e_collection = e_collection.get_collection(ele_type, ele_category)

    return DateDataCollection(start_date, end_date, granularity, filtered_e_collection)


def graph(date_data_collection):
    
    start_date, end_date, granularity, filtered_e_collection = date_data_collection

    img_data = io.BytesIO()

    amortization_total_sum, amortization_date_value = filtered_e_collection.amortization(start_date, end_date, granulation=granularity)
    amortization = AmortizationCollection(amortization_total_sum, amortization_date_value)

    costs_special, costs_regular = (filtered_e_collection.costs(start_date, end_date, granulation=granularity))
    costs = ReturnsCostsCollection(costs_special, costs_regular)

    returns_special, returns_costs = filtered_e_collection.costs(start_date, end_date, granulation=granularity)
    returns = ReturnsCostsCollection(returns_special, returns_costs)
    
    x_amortization = list(amortization.date_value.keys())
    y_amortization = list(map(lambda x: x[1], amortization.date_value.values()))

    x_costs_special = list(costs.special[1].keys())
    y_costs_special = list(map(lambda x: x[1], costs.special[1].values()))

    x_costs_regular = list(costs.regular[1].keys())
    y_costs_regular = list(map(lambda x: x[1], costs.regular[1].values()))
    
    x_returns_special = list(returns.special[1].keys())
    y_returns_special = list(map(lambda x: x[1], returns.special[1].values()))

    x_returns_regular = list(returns.regular[1].keys())
    y_returns_regular = list(map(lambda x: x[1], returns.regular[1].values()))
       
    plt.plot(x_amortization, y_amortization, label="amortization")
    plt.plot(x_costs_special, y_costs_special, label="costs special")
    plt.plot(x_costs_regular, y_costs_regular, label="costs regular")

    plt.plot(x_returns_special, y_returns_special, label="returns special")
    plt.plot(x_returns_regular, y_returns_regular, label="returns regular")

    plt.title("asdf")
    plt.legend()
    #plt.show()
    plt.savefig(img_data, orientation='landscape', transparent=True, format='svg')
    img_data.seek(0)

    return img_data

def make_html_page(img_data):

    encoded = base64.encodestring(img_data.read())    

    TEMPLATE= ("<html> <body> <img src=\"data:image/svg+xml;base64,{0}\"/> </body> </html>".format(encoded.decode('utf8')))

    return TEMPLATE

if __name__ == '__main__':

    try:
        parsed = parser.parse_args()
        a = make_data(parsed)
        img_data = graph(a)
        html_page = make_html_page(img_data)

        with open(parsed.output_file, 'w') as f:
            f.write(html_page)

    except (ImportError, ModuleNotFoundError) as e:
        print(e, file=sys.stderr)
        dependencies = "Dependencies: Matplotlib + pylab, dateutil"
        print(dependencies, file=sys.stderr)


