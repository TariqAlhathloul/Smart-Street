"""
set of tools to help LLM model to calculate total number of violations in a time period,
the description of each function is typed to clear for the model when to use it.

please refer to the documentation for more information on how to use the tools.
https://python.langchain.com/docs/how_to/custom_tools/
"""
import pandas as pd
import numpy as np
from langchain_core.tools import tool

@tool
def calculate_total_violations(violations: list) -> int:
    """
    total number of violations
    """
    return len(violations)

@tool
def calculate_violations_by_type(violations: list) -> int:
    """
    total number of violations by type
    """
    violations_by_type=violations['violation_type'].value_counts()
    return violations_by_type


@tool
def calculate_violations_by_time_interval(violations: list, start_date: str, end_date: str) -> int:
    """
    total number of violations by time interval
    """
    total_violations_by_time_interval = np.where(violations['date'] >= start_date) and np.where(violations['date'] <= end_date)

    return len(total_violations_by_time_interval)

@tool
def calculate_violations_by_street_name(violations: list, street_name: str) -> int:
    """
    total number of violations by street name
    """
    total_violations_by_street_name = violations[violations['street_name'] == street_name]
    return len(total_violations_by_street_name)