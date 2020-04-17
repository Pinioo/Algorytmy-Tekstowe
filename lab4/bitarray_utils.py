from bitarray import bitarray

def int2ba(val, l=None):
    to_return = bitarray()
    while val > 0:
        to_return.insert(0, True if val % 2 == 1 else False)
        val = int(val/2)
    if l is not None:
        while len(to_return) < l:
            to_return.insert(0, False) 
    return to_return

def ba2int(ba):
    to_return = 0
    for bit in ba:
        to_return *= 2
        to_return += 1 if bit else 0
    return to_return