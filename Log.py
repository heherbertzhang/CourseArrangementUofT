def printValue(val):
    return str(val[0]) + "," + str(val[1])
def printdomain(domain):
    return [printValue(v) for v in domain]