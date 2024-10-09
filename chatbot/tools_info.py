from tools import calculate_violations_by_street_name, calculate_total_violations, calculate_violations_by_time_interval, calculate_violations_by_type

#tools = [calculate_violations_by_street_name, calculate_total_violations, calculate_violations_by_time_interval, calculate_violations_by_type]
tools = [from tools import *]

for tool in tools:
    print(f'Name: {tool.name}')
    print(f'Description: {tool.description}')
    print(f'Args: {tool.args}')
    print("_"*100)



"""
OUTPUT:

Name: calculate_violations_by_street_name
Description: total number of violations by street name
Args: {'violations': {'items': {}, 'title': 'Violations', 'type': 'array'}, 'street_name': {'title': 'Street Name', 'type': 'string'}}
____________________________________________________________________________________________________
Name: calculate_total_violations
Description: total number of violations
Args: {'violations': {'items': {}, 'title': 'Violations', 'type': 'array'}}
____________________________________________________________________________________________________
Name: calculate_violations_by_time_interval
Description: total number of violations by time interval
Args: {'violations': {'items': {}, 'title': 'Violations', 'type': 'array'}, 'start_date': {'title': 'Start Date', 'type': 'string'}, 'end_date': {'title': 'End Date', 'type': 'string'}}
____________________________________________________________________________________________________
Name: calculate_violations_by_type
Description: total number of violations by type
Args: {'violations': {'items': {}, 'title': 'Violations', 'type': 'array'}}
____________________________________________________________________________________________________
"""