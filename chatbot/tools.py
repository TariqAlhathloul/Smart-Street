"""
set of tools to help LLM model to calculate total number of violations in a time period,
the description of each function is typed to clear for the model when to use it.
"""
from langchain_core.tools import tool

@tool
def calculate_total_violations(violations: list) -> int:
    """
    total number of violations
    """
    return len(violations)

@tool
def calculate_violations_by_type(violations: list) -> dict:
    """
    total number of violations by type
    """
    violations_by_type = {}
    for violation in violations:
        violation_type = violation['violation_type']
        if violation_type not in violations_by_type:
            violations_by_type[violation_type] = 1
        else:
            violations_by_type[violation_type] += 1
    return violations_by_type