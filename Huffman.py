
import os
import heapq
import numpy as np

kodai = {}

class HuffmanCoding:
    def __init__(self, path, root=None):
        self.path = path # kelias iki failo kuris bus compressed
        self.heap = []   # to store priority queue
        self.codes = {}  # to store codes of letters
        self.reverse_mapping = {} # to store values of codes
        self.root = root

    class HeapNode:
        def __init__(self, char, freq): # pass char, freq
            self.char = char
            self.freq = freq
            self.left = None
            self.right = None

        ### for comparing two nodes:

        def __lt__(self,other): # less than
            return self.freq < other.freq

        def __eq__(self,other): # equal 
            if(other == None):
                return False
            if(not isinstance(other, HeapNode)):
                return False
            return self.freq == other.freq

    def make_frequency_dict(self,text):
        # raidziu dazniu dictionary
        frequency = {}
        for character in text:
            if not character in frequency:
                frequency[character] = 0  # jei nera tokio char, sukuria
            frequency[character] += 1 # increment count
        return frequency

    def make_heap(self, frequency):
        #make priority queue
        for key in frequency:
            node = self.HeapNode(key, frequency[key]) # create node and pass char
            heapq.heappush(self.heap, node)



    # extract two minimum nodes, merge, update priority queue - > tree
    def merge_codes(self):
        # build tree, save root node in heap
        while(len(self.heap)>1):
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)

            merged = self.HeapNode(None, node1.freq + node2.freq) # frequency is a sum of two nodes
            merged.left = node1
            merged.right = node2

            heapq.heappush(self.heap, merged) # push back to function
    
    def make_codes_helper(self, node, current_code):
        if(node == None): # not a leaf
            return
        if(node.char != None): # leaf node
            self.codes[node.char] = current_code
            self.reverse_mapping[current_code] = node.char

        self.make_codes_helper(node.left, current_code + "0") # append 0 when going left
        self.make_codes_helper(node.right, current_code + "1") # append 0 when going left


    def make_codes(self):
        #make codes for characters and save to codes
        root = heapq.heappop(self.heap) #start from root, left 0, right 1
        self.root = root
        current_code = ""
        self.make_codes_helper(root, current_code)

    def get_encoded_text(self, text):
        # replace character with its code
        encoded_text = ""
        for character in text:
            encoded_text += self.codes[character]
        return encoded_text

    def pad_encoded_text(self,encoded_text):
        # add extra dummy bits
        extra_padding = 8 - len(encoded_text) % 8 # needed dummy bits count
        for i in range(extra_padding):
            encoded_text += "0"
        
        padded_info = "{0:8b}".format(extra_padding)
        #print(padded_info)
        encoded_text = padded_info + encoded_text
        return encoded_text


    def get_byte_array(self, padded_encoded_text):
        # convert bits into bytes, retur byte array
        # take 8 bits at time, convert to byte and append to an array
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8] # substring of 8 bits
            b.append(int(byte, 2)) # covert 8 bit strings to actual byte
        return b

    def kurk_taisykle(self,masyvas2):  # paduodama kodavimo taisykle [[seka, koduote],[seka, koduote]]
        
        taisykle = ''
        nuliai = []
        vienetai = []

        for i in masyvas2:  # nuimama po pirma is kaires koduotes simboli ir priskiriama kurioje sakoje kabos seka
            if i[1][0] == '0':
                i[1] = i[1][1:]
                nuliai.append(i)
            else:
                i[1] = i[1][1:]
                vienetai.append(i)

        if len(nuliai) > 1:  # yra issisakojimas, i taisykle rasome 0 ir kvieciame rekursyviai zemesniai sakai
            taisykle += '0'
            a = self.kurk_taisykle(nuliai)
            taisykle += a
        else:  # liko 1 lapas, rasome 1 ir seka
            taisykle += '1' + nuliai[0][0]
        if len(vienetai) > 1:  # tas pats kaip su vienetais
            taisykle += '0'
            b = self.kurk_taisykle(vienetai)
            taisykle += b
        else:
            taisykle += '1' + vienetai[0][0]
        return taisykle  # grazina taisykle i virsune, ir ji prijungiama prie buvusios taisykles. 

    def compress(self):
        filename, file_extension = os.path.splitext(self.path) # splitina pavadinima ir extenstion
        output_path = filename + ".bin"

        with open(self.path, 'r+') as file, open(output_path, 'wb') as output: # write as binary
            text = file.read() # read text in input file
            text = text.rstrip() # istrint extra spaces??

            frequency = self.make_frequency_dict(text)

            self.make_heap(frequency)
            self.merge_codes()
            self.make_codes()

            encoded_text = self.get_encoded_text(text)
            padded_encoded_text = self.pad_encoded_text(encoded_text)
            
            data = list(self.codes.items())
            an_array = np.array(data)
            taisykle = self.kurk_taisykle(an_array)
            print(taisykle)

            b = self.get_byte_array(padded_encoded_text)
            output.write(bytes(b))

        print("Compressed")
        return output_path


    def remove_padding(self, bit_string):
        # remove padding 
        padded_info = bit_string[:8] #first 8 bits
        extra_padding = int(padded_info, 2)

        bit_string = bit_string[8:] # remove padded info, first 8 bits
        encoded_text = bit_string[:-1*extra_padding] # remove padded bits

        return encoded_text
    
    def decode_text(self, encoded_text):
        #decode characters
        current_code = ""
        decoded_text = ""

        for bit in encoded_text:
            current_code += bit
            if(current_code in self.reverse_mapping):
                character = self.reverse_mapping[current_code]
                decoded_text += character
                current_code = ""
        return decoded_text



    
    def decompress(self, input_path):
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + "_decompressed" + ".txt"
    
        

        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ""

            byte = file.read(1) # read one byte at time
            while(len(byte)>0): # while there are bytes left
                byte = ord(byte) # int value of unicode representation of byte?
                bits = bin(byte)[2:].rjust(8, '0') # bit values from given byte, appends 0b at start so we need to substring it
                bit_string += bits
                byte = file.read(1) # move on to next byte

            encoded_text = self.remove_padding(bit_string)
            decoded_text = self.decode_text(encoded_text)
      

            output.write(decoded_text)
        print("Decompressed")
        return output_path
    
    

import sys
import time

start = time.time()
path = "Huffman.py"

h = HuffmanCoding(sys.argv[1])
output_path = h.compress()


print("Compressed file path: " + output_path)
end = time.time()
print(end - start)
#start = time.time()
#decom_path = h.decompress(output_path)
#print("Decompressed file path: " + decom_path)
#end = time.time()
#print(end - start)
