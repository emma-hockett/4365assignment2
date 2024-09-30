import sys
import copy


# For reading the variable file
def read_varfile(varfile):
    vars = {}
    with open(varfile) as file:
        # For each variable, save the variable name and its domain
        for line in file:
            variable, domain = line.split(':')
            vars[variable.strip()] = list(map(int, domain.strip().split()))
    return vars


# For reading the constraints file
def read_confile(confile):
    cons = []
    with open(confile) as file:
        # For every constraint save the first variable, the operator, and the second variable
        for line in file:
            var1, operator, var2 = line.split()
            cons.append((var1, operator, var2))
    return cons


# Checks whether all variables have assignment
def isAssignmentComplete(vars, assignment):
    if len(assignment) == len(vars):
        return True
    return False


''' Selects the most constrained unassigned variable based on
    1) the smallest domain size
    2) if tied, then select by most constraining heuristic
    3) if tied, then select variable alphabetically
    
    Selects the value for the unassigned variable based on 
    1) the least constraining value
    2) if tied, favor the lower value
'''


def selectMostConstrained(vars, cons, assignment):
    smallestDomainSize = float('inf')
    tiedVars = {}

    # Find the most constrained variables (the fewest domain values)
    for var in vars:
        if var not in assignment:
            domainSize = len(vars[var])
            if domainSize < smallestDomainSize:
                smallestDomainSize = domainSize
                tiedVars = {var: vars[var]}  # Clear and add most constrained
            elif domainSize == smallestDomainSize:
                tiedVars[var] = vars[var]

    # No tie present, return the most constrained variable
    if len(tiedVars) == 1:
        return next(iter(tiedVars))

    # Apply most constraining heuristic to break ties
    constraintCount = {var: 0 for var in tiedVars}

    for con in cons:
        var1, _, var2 = con
        if var1 in tiedVars and var2 not in assignment:
            constraintCount[var1] += 1
        if var2 in tiedVars and var1 not in assignment:
            constraintCount[var2] += 1

    # Find the most constraining variable
    mostConstrainedVar = max(constraintCount, key=constraintCount.get)

    return mostConstrainedVar


# Checks if the assignments are consistent with constraints
def isConsistentWithConstraints(assignment, cons):
    for con in cons:
        var1, op, var2 = con

        if var1 in assignment and var2 in assignment:
            if op == '=':
                if assignment[var1] != assignment[var2]:
                    return False
            elif op == '>':
                if assignment[var1] <= assignment[var2]:
                    return False
            elif op == '<':
                if assignment[var1] >= assignment[var2]:
                    return False
            elif op == '!':
                if assignment[var1] == assignment[var2]:
                    return False
    return True


# Select the least constraining value, such that it leaves other variables the most options
def findLeastConstrainingValue(vars, var, cons, assignment):
    """
        Returns the values in the domain of `var` in order of least constraining.
    """
    domain = vars[var]
    constraint_count = []

    for value in domain:
        count = 0
        temp_assignment = assignment.copy()
        temp_assignment[var] = value

        # For each value, count how many variables it constrains in the future
        for con in cons:
            var1, op, var2 = con

            # If the one being tested is the first in the constraint, check it's temporary assignment against all values of the other variable in the constraint
            if var1 == var and var2 not in assignment:
                valid_values = 0
                for other_value in vars[var2]:
                    #If there is a valid value for the unassigned variable against the temp then increase the valid value count
                    if isConsistentWithSingleValue(temp_assignment[var1], op, other_value):
                        valid_values += 1
                count += valid_values
            # If the one being tested is the second in the constraint, check it's temporary assignment against all values of the other variable in the constraint
            elif var2 == var and var1 not in assignment:
                valid_values=0
                for other_value in vars[var1]:
                    # If there is a valid value for the unassigned variable against the temp then increase valid value count
                    if isConsistentWithSingleValue(other_value, op, temp_assignment[var2]):
                        valid_values += 1
                count += valid_values

        constraint_count.append((value, count))

    # Sort the domain by the most valid values left for the unassigned variables
    sorted_values = sorted(constraint_count, key=lambda x: (-x[1], x[0]))

    # Return only the values, sorted by least constraining
    return [val for val, _ in sorted_values]


def isConsistentWithSingleValue(temp_assignment, op, other_value):
    # Checks the temporary assignment against the values from the unassigned variable
    if op == '=':
        return temp_assignment == other_value
    elif op == '>':
        return temp_assignment > other_value
    elif op == '<':
        return temp_assignment < other_value
    elif op == '!':
        return (temp_assignment!= other_value)
    return True


# Backtracking without forward checking algorithm
def backTracking(vars, cons, assignment, branch_count=[1], path=""):

    allValuesTried = False
    outString = ""

    # If the assignment is complete and consistent with constraints, return the solution
    if isAssignmentComplete(vars, assignment):
        if isConsistentWithConstraints(assignment, cons):

            outString = f"{branch_count[0]}. " + ', '.join([f"{var}={assignment[var]}" for var in assignment]) + " solution"
            print(outString)
            return assignment, False

    # Select the most constrained unassigned variable
    unassignedVar = selectMostConstrained(vars, cons, assignment)
    values = findLeastConstrainingValue(vars, unassignedVar, cons, assignment)

    valuesLeftToTry = len(values)

    # Get the least constraining values for the variable
    for domainValue in values:

        current_path = f"{path}, {unassignedVar}={domainValue}" if path else f"{unassignedVar}={domainValue}"
        assignment[unassignedVar] = domainValue
        values = findLeastConstrainingValue(vars, unassignedVar, cons, assignment)

        # Check if the current assignment is consistent
        if isConsistentWithConstraints(assignment, cons):
            result, valuesLeft = backTracking(vars, cons, assignment, branch_count, current_path)
            if result is not None:
                return result, False
            if valuesLeft == True:
                allValuesTried = True

        # No valid assignment found for this path
        if not allValuesTried or valuesLeftToTry == 1:
            outString = f"{branch_count[0]}. " + ', '.join([f"{var}={assignment[var]}" for var in assignment]) + " failure"
            print(outString)
            branch_count[0] += 1

        valuesLeftToTry -= 1
        # Backtrack
        assignment.pop(unassignedVar)

    if valuesLeftToTry == 0:
        return None, True

    return None, False


""" 
    Reduce the domains of unassigned variables
    that are inconsistent with constraints.
"""
def forwardCheck(assignedVar, assignedValue, domains, cons, assignment):
    newDomains = copy.deepcopy(domains)
    for con in cons:
        var1, op, var2 = con[0], con[1], con[2]
        if var1 == assignedVar and var2 not in assignment:
            newDomain = []
            for value in newDomains[var2]:
                if satisfiesConstraint(assignedValue, op, value):
                    newDomain.append(value)
            # Fails if domain is empty
            if len(newDomain) == 0:
                return False
            newDomains[var2] = newDomain # Update the domain of unassigned variable

        elif var2 == assignedVar and var1 not in assignment:
            newDomain = []
            for value in newDomains[var1]:
                if satisfiesConstraint(value, op, assignedValue):
                    newDomain.append(value)
            if len(newDomain) == 0:
                return False
            newDomains[var1] = newDomain

    # Return the new domains
    return newDomains


def satisfiesConstraint(value1, op, value2):
    if op == '=':
        return value1 == value2
    elif op == '!':
        return value1 != value2
    elif op == '>':
        return value1 > value2
    elif op == '<':
        return value1 < value2
    return False


# Backtracking with forward checking algorithm
def forwardChecking(vars, cons, assignment, branch_count=[1]):

    """ Select a variable and assign it a value
        After assigning the variable to value,
        iterate over the unassigned variables constrained by that variable
        for each unassigned variable, remove values that are inconsistent with the assignment
        backtrack if the domain of the unassigned variables become empty
    """

    outString = ''

    # If the assignment is complete and consistent with constraints, return the solution
    if isAssignmentComplete(vars, assignment):
        if isConsistentWithConstraints(assignment, cons):
            outString = f"{branch_count[0]}. " + ', '.join([f"{var}={assignment[var]}" for var in assignment]) + " solution"
            print(outString)
            return assignment

    # Select the most constrained unassigned variable
    unassignedVar = selectMostConstrained(vars, cons, assignment)

    values = findLeastConstrainingValue(vars, unassignedVar, cons, assignment)
    domains = copy.deepcopy(vars)

    # Create a shallow copy to track domain values for unassigned variables
    for var in vars:
        domains[var] = vars[var]

    # Iterate through each value in order of the least constrained
    for value in values:
        assignment[unassignedVar] = value

        newDomains = forwardCheck(unassignedVar, value, domains, cons, assignment)
        if newDomains:
            # Recurse with updated assignments and domains
            resultExists = forwardChecking(newDomains, cons, assignment)
            if resultExists:
                return resultExists

        outString = f"{branch_count[0]}. " + ', '.join([f"{var}={assignment[var]}" for var in assignment]) + " failure"
        print(outString)

        # Backtrack
        del assignment[unassignedVar]
        branch_count[0] += 1

    # No solution
    return None


# Reading in the command line arguments and calling the functions
def main():
    if len(sys.argv) != 4:
        print("Usage: python main.py <varfile> <confile> <method>")
        sys.exit(1)

    # Reading in the command line arguments for the file names
    varfile = sys.argv[1]
    confile = sys.argv[2]
    method = sys.argv[3]

    # Parsing the files to extract the information
    vars = read_varfile(varfile)
    cons = read_confile(confile)

    # Depending on what the chosen method is, call the correct algorithm
    if method.lower() == "none":
        backTracking(vars, cons, {})
    elif method.lower() == "fc":
        forwardChecking(vars, cons, {})
    else:
        print("Unknown method")
        sys.exit(1)


if __name__ == "__main__":
    main()
