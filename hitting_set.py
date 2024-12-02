import itertools

def minimum_hitting_set(sets):
    total = set().union(*sets)
    for length in range(1, len(total)):
        combinations = itertools.combinations(total, length)
        for combination in combinations:
            for ancestor_set in sets:
                if len(ancestor_set.intersection(set(combination))) == 0:
                    break
            else:
                return combination

sets = [{1, 2}, {2, 3}]
print(minimum_hitting_set(sets))