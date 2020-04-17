import huffman
import adaptive_huffman
import os
import re

def compression_level(org_file, comp_file):
    return 1 - (os.path.getsize(comp_file)/os.path.getsize(org_file))

def static_huffman_test(filename):
    with open(filename) as in_f:
        content = in_f.read()
        codes, encoded = huffman.encode(content)
        decrypted = huffman.decode(encoded, huffman.tree_from_codes(codes))
        if decrypted == content:
            print(">>>>Static Huffman encoded succesfully!")
        else: 
            print("!!!!Static Huffman encoding failed")
    huffman.compress_file(filename)
    comp_level = compression_level(filename, filename + ".sthuff")
    print(f"<<<<Compression level: {comp_level}")

def adaptive_huffman_test(filename):
    with open(filename) as in_f:
        content = in_f.read()
        encoded = adaptive_huffman.encode(content)
        decrypted = adaptive_huffman.decode(encoded)
        if decrypted == content:
            print(">>>>Adaptive Huffman encoded succesfully!")
        else: 
            print("!!!!Adaptive Huffman encoding failed")
    adaptive_huffman.compress_file(filename)
    comp_level = compression_level(filename, filename + ".dyhuff")
    print(f"<<<<Compression level: {comp_level}")


test_subjects = ["test1.txt", "test2.txt", "test3.txt", "testHp.txt"]

def make_tests():
    for test_file in test_subjects:
        print(f"Tests for {test_file} of size {os.path.getsize(test_file)}")
        static_huffman_test(test_file)
        adaptive_huffman_test(test_file)
    

make_tests()