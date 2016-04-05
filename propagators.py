'''
This file will contain different constraint propagators to be used within
bt_search.

propagator == a function with the following template
    propagator(csp, newly_instantiated_variable=None)
        ==> returns (True/False, [(Variable, Value), (Variable, Value) ...])

    csp is a CSP object---the propagator can use this to get access to the
    variables and constraints of the problem. The assigned variables can be
    accessed via methods, the values assigned can also be accessed.

    newly_instaniated_variable is an optional argument.
    if newly_instantiated_variable is not None:
        then newly_instantiated_variable is the most
        recently assigned variable of the search.
    else:
        propagator is called before any assignments are made
        in which case it must decide what processing to do
        prior to any variables being assigned. SEE BELOW

    The propagator returns True/False and a list of (Variable, Value) pairs.

    Returns False if a deadend has been detected by the propagator.
        in this case bt_search will backtrack
    Returns True if we can continue.

    The list of variable values pairs are all of the values
    the propagator pruned (using the variable's prune_value method).
    bt_search NEEDS to know this in order to correctly restore these
    values when it undoes a variable assignment.

    NOTE propagator SHOULD NOT prune a value that has already been
    pruned! Nor should it prune a value twice

    PROPAGATOR called with newly_instantiated_variable = None
        PROCESSING REQUIRED:
            for plain backtracking (where we only check fully instantiated
            constraints) we do nothing...return (true, [])

            for forward checking (where we only check constraints with one
            remaining variable) we look for unary constraints of the csp
            (constraints whose scope contains only one variable) and we
            forward_check these constraints.

            for gac we establish initial GAC by initializing the GAC queue with
            all constaints of the csp

    PROPAGATOR called with newly_instantiated_variable = a variable V
        PROCESSING REQUIRED:
            for plain backtracking we check all constraints with V (see csp
            method get_cons_with_var) that are fully assigned.

            for forward checking we forward check all constraints with V that
            have one unassigned variable left

            for gac we initialize the GAC queue with all constraints containing
            V.
'''


def prop_BT(csp, newVar=None):
    '''Do plain backtracking propagation. That is, do no
    propagation at all. Just check fully instantiated constraints'''

    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []


def prop_FC(csp, newVar=None):
    '''Do forward checking.  That is, check constraints with only one
    uninstantiated variable, and prune appropriately.  (i.e., do not prune a
    value that has already been pruned; do not prune the same value twice.)
    Return if a deadend has been detected, and return the variable/value pairs
    that have been pruned.  See beginning of this file for complete description
    of what propagator functions should take as input and return.

    Input: csp, (optional) newVar.
        csp is a CSP object---the propagator uses this to
        access the variables and constraints.

        newVar is an optional argument.
        if newVar is not None:
            then newVar is the most recently assigned variable of the search.
            run FC on all constraints that contain newVar.
        else:
            propagator is called before any assignments are made in which case
            it must decide what processing to do prior to any variable
            assignment.

    Returns: (boolean,list) tuple, where list is a list of tuples:
             (True/False, [(Variable, Value), (Variable, Value), ... ])

        boolean is False if a deadend has been detected, and True otherwise.

        list is a set of variable/value pairs that are all of the values the
        propagator pruned.
    '''
    pruned = []
    constraints = []
    if newVar:
        constraints = csp.get_cons_with_var(newVar)
    else:
        # the new var is None
        # check the constraints that has only one variable
        constraints = csp.get_all_cons()
    unassignedIndex = 0
    for constraint in constraints:
        if constraint.get_n_unasgn() == 1:
            vars = constraint.get_scope()
            vals = []
            for i, var in enumerate(vars):
                if not var.is_assigned():
                    unassignedVar = var
                    unassignedIndex = i
                    vals.append(0)
                else:
                    vals.append(var.get_assigned_value())
            # test the constraint with string the value in the domain of the only unassigned variable
            cur_dom = unassignedVar.cur_domain()
            for val in cur_dom:
                vals[unassignedIndex] = val
                if not constraint.check(vals):
                    unassignedVar.prune_value(val)
                    pruned.append((unassignedVar, val))
            if len(unassignedVar.cur_domain()) == 0:
                # Domain wiped out
                return False, pruned

    return True, pruned


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation, as described in lecture. See beginning of this file
    for complete description of what propagator functions should take as input
    and return.

    Input: csp, (optional) newVar.
        csp is a CSP object---the propagator uses this to access the variables
        and constraints.

        newVar is an optional argument.
        if newVar is not None:
            do GAC enforce with constraints containing newVar on the GAC queue.
        else:
            Do initial GAC enforce, processing all constraints.

    Returns: (boolean,list) tuple, where list is a list of tuples:
             (True/False, [(Variable, Value), (Variable, Value), ... ])

    boolean is False if a deadend has been detected, and True otherwise.

    list is a set of variable/value pairs that are all of the values the
    propagator pruned.
    '''

    '''
    pruned = []
    constraints = []
    gac_queue = []
    checked_gac_queue = []
    if newVar:
        constraints = csp.get_cons_with_var(newVar)
    else:
        # for gac we establish initial GAC by initializing the GAC queue with
        #all constaints of the csp
        constraints = csp.get_all_cons()
    gac_queue = list(constraints)
    while gac_queue:
        constraint = gac_queue.pop(0) #get the first gac constraint
        checked_gac_queue.append(constraint)
        for var in constraint.get_scope():
            for val in var.cur_domain():
                if not constraint.has_support(var, val):
                    var.prune_value(val)
                    pruned.append(var, val)
                    #check if there is new gac constraint resulted
                    for constraint in checked_gac_queue:
                        if var in constraint.get_scope():
                            gac_queue.append(constraint)
    '''
    pruned = []
    constraints = []
    gac_queue = []
    checked_gac_queue = []
    if newVar:
        constraints = csp.get_cons_with_var(newVar)
    else:
        # for gac we establish initial GAC by initializing the GAC queue with
        # all constaints of the csp
        constraints = csp.get_all_cons()
    gac_queue = [(var, constraint) for constraint in constraints \
                 for var in constraint.get_scope()]

    while gac_queue:
        is_shrinked_domain = False
        var, constraint = gac_queue.pop(0)  # get the first gac constraint
        for val in var.cur_domain():
            if not constraint.has_support(var, val):
                var.prune_value(val)
                pruned.append((var, val))
                #print("pruned, ", val)
                if len(var.cur_domain()) == 0:
                    # Domain wiped out
                    return False, pruned
                else:
                    is_shrinked_domain = True

        if is_shrinked_domain:
            # check if there is new gac constraint resulted
            i = 0

            for c in csp.get_cons_with_var(var):
                for v in c.get_scope():
                    if not v == var:
                        if (v,c) not in gac_queue:
                            gac_queue.append((v,c))
            '''
            for checked_var, checked_constraint in checked_gac_queue:
                if var in checked_constraint.get_scope() and not checked_var == var:
                    gac_queue.append(checked_gac_queue.pop(i))  # remove from checked and add to unchecked gac
                i += 1
            '''
        # add this constraint to checked
        checked_gac_queue.append((var, constraint))

    return True, pruned
