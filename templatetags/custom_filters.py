import ast  # This module helps safely evaluate strings containing Python literals

from django import template

register = template.Library()

@register.filter(name='parse_list')
def parse_list(value):
    try:
        # Safely evaluate the string as a Python literal (list)
        # Only works if the string is a valid Python literal.
        list_values = ast.literal_eval(value)
        # Check if it's actually a list
        if isinstance(list_values, list):
            # Join the list into a string with a comma and space
            return ', '.join(list_values)
        return value
    except (ValueError, SyntaxError):
        # In case it's not a valid Python literal or not a list
        return value
