
def mean(X):
    n = len(X)
    if n > 0:
        return float(sum(X)) / float(len(X))
    return 0


def median(X):
    n = len(X)
    if n == 0:
        return 0
    L = sorted(X)
    if n % 2:
        return L[n / 2]
    return mean(L[(n / 2) - 1:(n / 2) + 1])

def mode(X):
    n = len(X)
    if n == 0:
        return []

    d = {}
    for item in X:
        if d.has_key(item):
            d[item] += 1
        else:
            d[item] = 1

    #Added for Mode Function
    #Mode max number of occurrences initialized to 1
    m = [1]
    for key in d.keys():
        if d[key] > m[0]:
            m = [d[key], key]
        elif d[key] == m[0]:
            m.append(key)
    return m[1:]

