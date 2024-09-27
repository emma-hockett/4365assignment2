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
    unassignedVar = ''
    smallestDomainSize = float('inf')
    tiedVars = {}

    # Find the most constrained variables (the fewest domain values)
    for var in vars:
        # Check only unassigned variables
        if var not in assignment:
            domainSize = len(vars[var])
            if domainSize < smallestDomainSize:
                smallestDomainSize = domainSize
                unassignedVar = var
                # Clear existing values in dictionary and set new most constrained
                tiedVars = {unassignedVar: vars[var]}
            elif domainSize == smallestDomainSize:
                # Track tied variables
                tiedVars[var] = vars[var]

    # No tie is present, return the most constrained variable
    if len(tiedVars) == 1:
        return unassignedVar

    # Apply most constraining heuristic to break ties
    constraintCount = {}
    for var in tiedVars:
        constraintCount[var] = 0

    for con in cons:
        var1, op, var2 = con[0], con[1], con[2]
        if var1 in tiedVars and var2 not in assignment:
            constraintCount[var1] += 1
        if var2 in tiedVars and var1 not in assignment:
            constraintCount[var2] += 1

    # Find the most constraining variable (the highest constraint count)
    highestConstraints = max(constraintCount.values())
    tiedVars.clear()
    for var in constraintCount:
        if constraintCount[var] == highestConstraints:
            tiedVars[var] = constraintCount[var]

    # Break ties alphabetically if necessary
    if len(tiedVars) > 1:
        # Return alphabetically, the smallest variable
        return min(tiedVars.keys())

    # Return the most constraining variable
    return list(tiedVars.keys())[0]


# Checks if the assignments are consistent with constraints
def isConsistentWithConstraints(assignment, cons):
    for con in cons:
        var1, op, var2 = con[0], con[1], con[2]

        if var1 in assignment and var2 in assignment:
        # Check constraints on var1 and var2
            if op == '==':
                if assignment[var1] != assignment[var2]:
                    return False
            elif op == '!':
                if assignment[var1] == assignment[var2]:
                    return False
            elif op == '>':
                if assignment[var1] <= assignment[var2]:
                    return False
            elif op == '<':
                if assignment[var1] >= assignment[var2]:
                    return False
    return True


# Backtracking without forward checking algorithm
def backTracking(vars, cons, assignment, branch_count=[1], path=""):
    """
    Pseudocode:

    Backtracking(assignment, csp):
        If assignment is complete then return assignment
        var <-- select one unassigned variable
        for each value in the domain of var do
            if value is consistent with assignment then
                add {var = value} to assignment
                result <-- Backtrack(assginment, csp)
                if result != failure then
                    return result
                remove {var = value} from assignment
            return failure
    """

    # If assignment complete then return assignment
    if isAssignmentComplete(vars, assignment):
        print(f"{branch_count[0]}. {path} solution")
        return assignment

    # Select most constrained unassigned variable
    unassignedVar = selectMostConstrained(vars, cons, assignment)

    for domainValue in vars[unassignedVar]:

        current_path = f"{path}, {unassignedVar}={domainValue}" if path else f"{unassignedVar}={domainValue}"
        assignment[unassignedVar] = domainValue

        # Check if assignment is consistent
        if isConsistentWithConstraints(assignment, cons):
            result = backTracking(vars, cons, assignment, branch_count, current_path)
            if result is not None:
                return result
        else:
            print(f"{branch_count[0]}. {current_path} failure")
            branch_count[0] += 1

        # Backtrack due to failure
        assignment.pop(unassignedVar)

    # Failure
    return None

    #
    # """
    # Select one unassigned variable to be the current var, based on the most constrained heuristic. If tied then considers most constraining variable. If still tied then alphabetical
    # """
    # most_constrained_var = None
    # most_constrained_domain = float('inf')
    # for var, domain in vars.items():
    #     # If the current variable is more constrained than the previously most constrained variable then it becomes the most constrained variable
    #     if len(domain) < most_constrained_domain:
    #         most_constrained_domain = len(domain)
    #         most_constrained_var = var
    #     # If the current variable has the same domain, then tiebreaker is the most constraining variable
    #     elif len(domain) == most_constrained_domain:
    #         current_var_count = 0
    #         mcv_count = 0
    #         for con in cons:
    #             if var in con:
    #                 current_var_count += 1
    #             if most_constrained_var in con:
    #                 mcv_count +=1
    #         # If the current variable is more constraining than it becomes the variable to be used, otherwise stays the same (if same reverts to alphabetical)
    #         if current_var_count > mcv_count:
    #             most_constrained_var = var


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
    if method == "none":
        backTracking(vars, cons, {})
    elif method == "fc":
        forwardChecking(vars, cons, {})
    else:
        print("Unknown method")
        sys.exit(1)


if __name__ == "__main__":
    main()
