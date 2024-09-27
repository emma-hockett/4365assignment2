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


# Selects the most constrained unassigned variable
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
            if op == '==':
                if assignment[var1] != assignment[var2]:
                    return False
            elif op == '>':
                if assignment[var1] <= assignment[var2]:
                    return False
            elif op == '<':
                if assignment[var1] >= assignment[var2]:
                    return False
            elif op == '!=':
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

    # Sort the domain by the least constraining values (fewest future constraints)
    sorted_values = sorted(constraint_count, key=lambda x: (x[1], x[0]))

    # Return only the values, sorted by least constraining
    return [val for val, _ in sorted_values]

def isConsistentWithSingleValue(assignment, con, other_value):
    var1, op, var2 = con
    if var1 in assignment and op == '==':
        return assignment[var1] == other_value
    elif var1 in assignment and op == '>':
        return assignment[var1] > other_value
    elif var1 in assignment and op == '<':
        return assignment[var1] < other_value
    elif var1 in assignment and op == '!=':
        return assignment[var1] != other_value
    return True


# Backtracking without forward checking algorithm
def backTracking(vars, cons, assignment, branch_count=[1], path=""):
    outString = ""

    # If the assignment is complete, return the solution or a failure
    if isAssignmentComplete(vars, assignment):
        if isConsistentWithConstraints(assignment, cons):
            # Print and return solution
            outString = f"{branch_count[0]}. " + ', '.join([f"{var}={assignment[var]}" for var in assignment]) + " solution"
            print(outString)
            return assignment

    # Select the most constrained unassigned variable
    unassignedVar = selectMostConstrained(vars, cons, assignment)

    values = findLeastConstrainingValue(vars, unassignedVar, cons, assignment)
    valuesLeftToTry = len(values)

    # Get the least constraining values for the variable
    for domainValue in values:
        # Make a new assignment
        current_path = f"{path}, {unassignedVar} = {domainValue}" if path else f"{unassignedVar}={domainValue}"
        assignment[unassignedVar] = domainValue

        # Check if the current assignment is consistent
        if isConsistentWithConstraints(assignment, cons):
            result = backTracking(vars, cons, assignment, branch_count, current_path)
            if result is not None:
                return result


        # If no valid assignment found for this path, print failure (for partial assignments)
        if valuesLeftToTry != 0:
            outString = f"{branch_count[0]}. " + ', '.join([f"{var}={assignment[var]}" for var in assignment]) + f" failure"
            print(outString)
            branch_count[0] += 1

        # Backtrack by removing the variable from the assignment
        assignment.pop(unassignedVar)

    return None


# Backtracking with forward checking algorithm
def forwardChecking(vars, cons):
    """
        Backtracking with forward checking
    """


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
