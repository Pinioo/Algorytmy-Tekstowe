import heapq
from draw_huff import draw_huff
from bitarray_utils import *
import os


class HuffNode:
    def __init__(self, letter = None, cost = 0):
        self.letter = letter
        self.cost = cost
        self.left = None
        self.right = None
        self.parent = None

    def code(self):
        if self.parent is None:
            return bitarray()
        if self == self.parent.left:
            return self.parent.code() + bitarray('0')
        else:
            return self.parent.code() + bitarray('1')
        
    def is_leaf(self):
        return self.left is None

    def add_right(self, node):
        self.right = node
        node.parent = self

    def add_left(self, node):
        self.left = node
        node.parent = self


def static_huff_codes(root: HuffNode, code = bitarray()):
    if root.letter is not None:
        return {root.letter: code}
    else:
        return {**static_huff_codes(root.left, code + bitarray('0')), **static_huff_codes(root.right, code + bitarray('1'))}


def tree_from_codes(codes):
    root = HuffNode()
    for letter, code in codes.items():
        current_node = root
        for bit in code:
            if bit == False:
                if current_node.left is None:
                    current_node.add_left(HuffNode())
                current_node = current_node.left
            else:
                if current_node.right is None:
                    current_node.add_right(HuffNode())
                current_node = current_node.right
        current_node.letter = letter
    return root


def encode(text, draw_tree = False):
    costs = calculate_letter_cost(text)
    tree_set = set([HuffNode(key, cost) for key, cost in costs.items()])
    while len(tree_set) > 1:
        trees_to_join = heapq.nsmallest(2, tree_set, key=lambda node: node.cost)
        tree_set.remove(trees_to_join[0])
        tree_set.remove(trees_to_join[1])

        new_node = HuffNode()
        new_node.add_left(trees_to_join[0])
        new_node.add_right(trees_to_join[1])
        new_node.cost = new_node.left.cost + new_node.right.cost

        tree_set.add(new_node)
    root = tree_set.pop()
    if draw_tree:
        draw_huff(root)

    encoded = bitarray('')
    codes = static_huff_codes(root)
    for letter in text:
        encoded += codes[letter]

    return (codes, encoded) 


def decode(encoded, root):
    text = ""
    current_node = root
    for bit in encoded:
        if bit == False:
            current_node = current_node.left
        else:
            current_node = current_node.right
        if current_node.is_leaf():
            text += current_node.letter
            current_node = root
    return text

    
def calculate_letter_cost(text):
    costs = {}
    for letter in text:
        if letter not in costs:
            costs[letter] = 1
        else:
            costs[letter] += 1
    return costs


# File structure
# 1. 8 bits = number of codes
# 2. 8 bits = number of bits in the longest code
# 3. 3 bits for number of bits which means nothing at the end 
# 4+. letter + code length + code
def coded_to_file(encoded, codes, filename):
    longest_code = 0
    for code in codes.values():
        if len(code) > longest_code:
            longest_code = len(code)
    with open(filename, "wb") as file:
        ba_to_save = bitarray()
        ba_to_save += int2ba(len(codes), 8)
        
        bits_for_length = len(int2ba(longest_code))
        ba_to_save += int2ba(bits_for_length, 8)
        bits_to_save = 3 + len(encoded)
        for _, code in codes.items():  
            bits_to_save += 8 + bits_for_length + len(code)
        
        blank_bits = (8 - bits_to_save % 8) % 8
        ba_to_save += int2ba(blank_bits, 3)

        for letter, code in codes.items():
            letter_bits = bitarray()
            letter_bits.fromstring(letter)
            ba_to_save += letter_bits
            ba_to_save += int2ba(len(code), bits_for_length)
            ba_to_save += code
        ba_to_save += encoded
        ba_to_save += bitarray(blank_bits*'0')
        ba_to_save.tofile(file)


def decode_file(filename):
    longest_code = 0
    with open(filename, "rb") as file:
        ba = bitarray()
        ba.fromfile(file)
        codes_count = ba2int(ba[:8])
        longest_code = ba2int(ba[8:16])
        blank_bits = ba2int(ba[16:19])
        index = 19
        codes = {}
        for _ in range(codes_count):
            letter = ba[index:index+8].tostring()
            index += 8
            code_len = ba2int(ba[index:index+longest_code])
            index += longest_code
            code = ba[index:index+code_len]
            codes[letter] = code 
            index += code_len

        encoded = ba[index:-blank_bits]
        tree = tree_from_codes(codes)
        return decode(encoded, tree)


def compress_file(file_in, file_out=None):
    if file_out is None:
        file_out = file_in + ".sthuff"
    with open(file_in) as in_f:
        codes, encoded = encode(in_f.read())
        coded_to_file(encoded, codes, file_out)