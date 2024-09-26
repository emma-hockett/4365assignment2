import sys

# For reading the variable file
def read_var(varfile):
    vars = {}
    with open(varfile, 'r') as file:
        for line in file:
            variable, domain = line.split(':')
            vars[variable.strip()] = list(map(int, domain.strip().split()))
    return vars

# For reading the constraints file
def read_con(confile):
    cons = []
    with open(confile, 'r') as file:
        for line in file:
            var1, operator, var2 = line.split()
            cons.append((var1, operator, var2))
    return cons

# Backtracking without forward checking algorithm
def backTracking(vars, cons):
    """
    Pseudocode:

    Backtracking(assignmnet, csp):
        If assignemnt is complete then return assignment
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

# Backtracking with forward checking algorihtm
def forwardChecking(vars, cons):


# Reading in the command line arguments and calling the functions
def main():
    if len(sys.argv) != 4:
        print("Usage: python main.py <varfile> <confile> <method>")
        sys.exit(1)

    # Reading in the command line argument and calling methods to parse them
    varfile = sys.argv[1]
    confile = sys.argv[2]
    method = sys.argv[3]

    vars = read_var(varfile)
    cons = read_con(confile)

    # Depending on what the chosen method is, call the correct algorithm
    if method == "none":
        print("With backtracking")
        backTracking(vars, cons)
    elif method == "fc":
        print("With forward checking")
        forwardChecking(vars, cons)
    else:
        print("Unknown method")
        sys.exit(1)


if __name__ == "__main__":
    main()
