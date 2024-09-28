import sys


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

            if var1 == var and var2 not in assignment:
                for other_value in vars[var2]:
                    if not isConsistentWithSingleValue(temp_assignment, con, other_value):
                        count += 1
            elif var2 == var and var1 not in assignment:
                for other_value in vars[var1]:
                    if not isConsistentWithSingleValue(temp_assignment, con, other_value):
                        count += 1

        constraint_count.append((value, count))

    # Sort the domain by the least constraining values (the fewest future constraints)
    sorted_values = sorted(constraint_count, key=lambda x: (x[1], x[0]))

    # Return only the values, sorted by least constraining
    return [val for val, _ in sorted_values]


def isConsistentWithSingleValue(assignment, con, other_value):
    var1, op, var2 = con
    if var1 in assignment and op == '=':
        return assignment[var1] == other_value
    elif var1 in assignment and op == '>':
        return assignment[var1] > other_value
    elif var1 in assignment and op == '<':
        return assignment[var1] < other_value
    elif var1 in assignment and op == '!':
        return assignment[var1] != other_value
    return True


# Backtracking without forward checking algorithm
def backTracking(vars, cons, assignment):
    allValuesTried = False
    outString = ""

    # If the assignment is complete and consistent with constraints, return the solution
    if isAssignmentComplete(vars, assignment):
        if isConsistentWithConstraints(assignment, cons):
            for var in assignment:
                outString += var + " = " + str(assignment[var]) + ", "
            outString = outString[0:len(outString)-2]
            outString += "  solution"
            print(outString)
            return assignment, False

    # Select the most constrained unassigned variable
    unassignedVar = selectMostConstrained(vars, cons, assignment)

    values = findLeastConstrainingValue(vars, unassignedVar, cons, assignment)
    valuesLeftToTry = len(values)

    # Get the least constraining values for the variable
    for domainValue in values:
        assignment[unassignedVar] = domainValue

        # Check if the current assignment is consistent
        if isConsistentWithConstraints(assignment, cons):
            result, valuesLeft = backTracking(vars, cons, assignment)
            if result is not None:
                return result, False
            if valuesLeft == True:
                allValuesTried = True

        # No valid assignment found for this path
        if not allValuesTried or valuesLeftToTry == 1:
            outString = ''
            for var in assignment:
                outString += var + " = " + str(assignment[var]) + ", "
            outString = outString[0:len(outString) - 2]
            outString += "  failure"
            print(outString)

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
    for con in cons:
        var1, op, var2 = con[0], con[1], con[2]
        newDomain = []
        if var1 == assignedVar and var2 not in assignment:
            for value in domains[var2]:
                newDomain.append(value)
            for value in domains[var2]:
                if not satisfiesConstraint(assignedValue, op, value):
                    newDomain.remove(value)

            # Failure if newDomain is empty
            if len(newDomain) == 0:
                return False
            else:
                # Update the domain
                domains[var2] = newDomain

        elif var2 == assignedVar and var1 not in assignment:
            for value in domains[var1]:
                newDomain.append(value)
            for value in domains[var1]:
                if not satisfiesConstraint(value, op, assignedValue):
                    newDomain.remove(value)

            if len(newDomain) == 0:
                return False
            else:
                # Update the domain
                domains[var1] = newDomain

    # New domain is not empty
    return True


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
def forwardChecking(vars, cons, assignment):

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
            for var in assignment:
                outString += var + " = " + str(assignment[var]) + ", "
            outString = outString[0:len(outString)-2]
            outString += "  solution"
            print(outString)
            return assignment

    # Select the most constrained unassigned variable
    unassignedVar = selectMostConstrained(vars, cons, assignment)

    values = findLeastConstrainingValue(vars, unassignedVar, cons, assignment)
    domains = {}

    # Create a shallow copy to track domain values for unassigned variables
    for var in vars:
        domains[var] = vars[var]

    # Iterate through each value in order of the least constrained
    for value in values:
        assignment[unassignedVar] = value

        forwardCheckSucceeded = forwardCheck(unassignedVar, value, domains, cons, assignment)
        if forwardCheckSucceeded:
            # Recurse with updated assignments and domains
            resultExists = forwardChecking(domains, cons, assignment)
            if resultExists:
                return resultExists

        outString = ''
        for var in assignment:
            outString += var + " = " + str(assignment[var]) + ", "
        outString = outString[0:len(outString) - 2]
        outString += "  failure"
        print(outString)

        # Backtrack
        del assignment[unassignedVar]

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
