from bitarray_utils import *
from draw_huff import draw_huff
import os
from collections import defaultdict

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

    def find_next_at_level(self, level):
        if level == 0:
            return self
        if self.left is not None:
            found = self.left.find_next_at_level(level+1)
            if found is not None:
                return found

            found = self.right.find_next_at_level(level+1)
            if found is not None:
                return found
        return None

    def right_sibling(self):
        current_node = self
        level = 0
        while current_node.parent is not None:
            if current_node == current_node.parent.left:
                found = current_node.parent.right.find_next_at_level(level)
                if found is not None:
                    return found
            current_node = current_node.parent
            level -= 1
            
        current_node = self
        depth = 0
        while current_node.parent is not None:
            current_node = current_node.parent
            depth += 1
        found = current_node.find_next_at_level(-depth+1)
        if found is not None:
            return found
        return None

    def swap(self, other):
        self.parent, other.parent = other.parent, self.parent

        if self.parent is not None:
            if self.parent.left == other:
                self.parent.left = self
            else:
                self.parent.right = self

        if other.parent is not None:
            if other.parent.left == self:
                other.parent.left = other
            else:
                other.parent.right = other

    def increment(self):
        self.cost += 1
        if self.parent is not None:
            right_sib = self.right_sibling()
            if right_sib.cost < self.cost:
                while True:
                    next_sib = right_sib.right_sibling()
                    if next_sib is None or right_sib.cost != next_sib.cost:
                        break
                    else:
                        right_sib = next_sib
                
                if right_sib != self.parent:
                    self.swap(right_sib)
            self.parent.increment()



def encode(text,draw_tree=False):
    encoded = bitarray()
    count = defaultdict(int)
    nodes = {"": HuffNode("")}
    root = nodes[""]
    for letter in text:
        if letter in nodes:
            node = nodes[letter]
            encoded += node.code()
            node.increment()
        else:
            updated_node = nodes[""]
            encoded += updated_node.code()
            encoded.fromstring(letter)
            node = HuffNode(letter, cost=1)
            nodes[letter] = node
            zero_node = HuffNode("")
            updated_node.add_left(zero_node)
            updated_node.add_right(node)
            nodes[""] = zero_node
            updated_node.increment()

    if draw_tree:
        draw_huff(root)
    return encoded


def decode(bitarr):
    decoded = ""
    count = defaultdict(int)
    nodes = {"": HuffNode("")}
    root = nodes[""]
    current_node = root
    bits = len(bitarr)
    index = 0
    while index <= bits:
        if current_node.is_leaf():
            if current_node.letter != "":
                decoded += current_node.letter
                current_node.increment()
            else:
                try:
                    letter = bitarr[index:index+8].tostring()
                except UnicodeDecodeError:
                    print(bitarr[index:index+8])
                    print(f"Index: {index}, Bits: {bits}")
                    raise ArithmeticError
                decoded += letter
                index += 8
                node = HuffNode(letter, cost=1)
                nodes[letter] = node
                zero_node = HuffNode("")
                current_node.add_left(zero_node)
                current_node.add_right(node)
                nodes[""] = zero_node
                current_node.increment()
            current_node = root
        if index < bits:
            current_node = current_node.right if bitarr[index] else current_node.left
        index += 1

    return decoded


def coded_to_file(encoded, filename):
    blank_bytes = (8 - (3 + len(encoded)) % 8) % 8
    to_save = int2ba(blank_bytes, 3) + encoded + bitarray(blank_bytes*'0')
    with open(filename, "wb") as file:
        to_save.tofile(file)


def decode_file(filename):
    with open(filename, "rb") as file:
        bitarr = bitarray()
        bitarr.fromfile(file)
        blank_bytes = ba2int(bitarr[:3])
        return decode(bitarr[3:-blank_bytes])


def compress_file(file_in, file_out=None):
    if file_out is None:
        file_out = file_in + ".dyhuff"
    with open(file_in) as in_f:
        encoded = encode(in_f.read())
        coded_to_file(encoded, file_out)
    