"""
huffmanCompressor.py
Author: Roman T

Experimental implementation of huffman compression using python

Provides the class Huffman() to handle compression and decompression of binary data and export results

When called as __main__ script uses argparse to accept command line arguments for operation
Arguments:
    input: (required) the file that will be fed into script for compression/decompression
    --compress, -c: (optional) sets script to compress input file
    --decompress, -d: (optional) sets script to decompress input file
    --out-file, -o: (optional) file that any script outputs will be written to
Note: --compress and --decompress cannot be called at the same time but one or the other is required
Note 2: when no out-file is specified the input file will be used as a base to generate an output file
"""


# imports
from pathlib import Path
from pickle import dumps, loads
import argparse

class Huffman:
    """
    Provides methods to compress and decompress binary data using Huffman compression
    Also has methods to handle incoming and outgoing data
    
    Methods:
        __init__: initializes class variables
        new_worker: sets new worker string and clears associated variables
        new_out: sets new output file
        export_product: saves product string to file or prints to stdout
        compress: compresses worker string using huffman tree that is created by function
        decompress: decompresses worker string
    """
    def __init__(self, content_in, file_out:Path = None):
        """
        Initializes class with all the primary variables that carry the compression/ decompression data
        The function requires a value for content_in however providing file_out is optional

        Arguments:
            content_in: data to be set as the functions working string
            file_out: (Optional) path that any output files should be written to
        """

        # placeholders
        self.worker: bytes = b""
        self.out_file: Path = None
        self.output: bytes = b""
        # comp_tools is all the elements that are created then used to compress the worker string (not used for decomp)
        self.comp_tools = {"frequency": {}, "tree": [], "trace": {}}

        self.new_worker(content_in)  # gets initial string to be worked on and loads to self.working_string
        if file_out:
            self.new_out(file_out)  # gets initial output file path and saves to self.out_file

    def new_worker(self, new_in):
        """
        Sets worker string using data from new_in
        Can take a string, bytestring/bytearray, and pathlib.Path object
        If new_in is a string, it is encoded to bytes using the .encode() method
        If new_string is bytes, it is saved directly to worker
        IF new_string is Path object, the files contents are read into worker using the .read_bytes() method

        Also resets output and comp_tools variables

        Arguments:
            new_in: content to be used to set worker
        """

        is_type = type(new_in)
        self.output = b""  # resets output since it is no longer associated with the worker
        self.comp_tools = {"frequency": {}, "tree": [], "trace": {}}  # resets comp_tools

        if issubclass(is_type, Path):  # if new_in is pathlib.Path, file is read in using read_bytes method
            if new_in.exists():
                self.worker = new_in.read_bytes()  # calls read_bytes() method to read binary from file
            else:
                raise FileNotFoundError(f"Could not find file \"{new_in}\"")

        elif is_type is bytes:  # if new_in is bytes the bytestring is stored directly
            self.worker = new_in

        elif is_type is str:  # if new_in is string the string is converted to bytes and stored
            self.worker = new_in.encode()

        else:
            raise TypeError(f"Could not import type {is_type}")

    def new_out(self, new_path:Path):
        """
        Sets path for exported files
        Takes a pathlib.Path object and saves it to self.out_file

        Can also set self.outfile to be None if new_path is set as False/None

        Arguments:
            new_path: pathlib.Path object to be set as out file path
        """
        if issubclass(type(new_path), Path):  # since Path creates subclass of windows or posix path, checks if object is subclass of Path
            self.out_file = new_path

        elif not new_path:  # self.out_file can be rest to blank if None or False are supplied as argument
            self.out_file = None
        else:  # raises exception if not of type False/ None or pathlib.Path object
            raise TypeError(f"Could not handle object of type {type(new_path)}")

    def export_product(self, alt_out:Path = None):
        """

        """
        if alt_out:
            self.new_out(alt_out)

        if self.out_file:
            print(f"Writing data to file \"{self.out_file}\"")
            self.out_file.write_bytes(self.output)
        else:
            print("No output file specified, data will be written to screen.")
            try:
                print(self.output.decode())
            except Exception:
                print("Encoding Error: Could not display content to screen")

    def compress(self, alt_in = None, alt_out:Path = None, export = True):

        # if alternate worker/out file are specified, call functions to set them as main
        if alt_in:
            self.new_worker(alt_in)
        if alt_out:
            self.new_out(alt_out)

        # -------------------- #
        # counts the occurrences of unique characters (bytes) in worker string and saves value to self.comp_tools
        working_frequency = {}
        for char in self.worker:
            if char in working_frequency:
                working_frequency[char] += 1
            else:
                working_frequency[char] = 1
        self.comp_tools["frequency"] = working_frequency

        # -------------------- #
        # creates huffman tree and associated trace dictionary using frequency dictionary

        # sorts from the highest frequency to the lowest
        # converts into tuple list with new dictionary that will be used to construct the trace dictionary
        sorted_frequency = \
            [(char[0], char[1], {char[0]: ""}) for char in sorted(self.comp_tools["frequency"].items(), key=lambda keys: keys[1], reverse=True)]

        # lambda function to update character trace with desired character
        char_count = lambda app_val, count_loc: {char: app_val + counter for char, counter in count_loc.items()}

        while len(sorted_frequency) > 2:  # loop runs until there are only 2 top level elements left
            set1, set2 = sorted_frequency.pop(-1), sorted_frequency.pop(-1)  # pops last two elements from list

            # creates new branch element
            branch_worker = [set1[0], set2[0]]  # new branch
            branch_freq = set1[1] + set2[1]  # new frequency for branch created by adding frequency of old elements
            char_tracker = char_count("0", set1[2]) | char_count("1", set2[2])  # updates trace dicts and combines into one

            new_branch = (branch_worker, branch_freq, char_tracker)  # combines work into complete new element
            sorted_frequency.append(new_branch)

            # resorts list for next run
            sorted_frequency = [char for char in
                                sorted(sorted_frequency, key=lambda keys: keys[1], reverse=True)]  # re-sorts

        self.comp_tools["tree"] = [branch[0] for branch in sorted_frequency]  # strips elements to pure branch lists
        self.comp_tools["trace"] = char_count("0", sorted_frequency[0][2]) | char_count("1", sorted_frequency[1][2])  # strips out and combines trace dicts

        # -------------------- #
        # converts self.worker to compressed form using trace dictionary

        encoded = "".join([self.comp_tools["trace"][char] for char in self.worker])

        # pads bits up to the nearest byte so things don't break
        # number of padded bytes is recorded and stored in binary data
        padding = 0
        while len(encoded) % 8 != 0:
            encoded += "1"
            padding += 1

        # at this point the string is ones and zeros (ie: "11010010")
        # separates string into 8 character chunks and converts into integer values, adding to a list
        chunked = [padding]  # the number of padding bits is the first byte in the array
        for chunk in range(0, len(encoded), 8):
            chunked.append(int(encoded[chunk:chunk + 8], 2))

        byte_convert = bytearray(chunked)  # converts list of ints into byte array

        # -------------------- #
        # adds huffman tree to start of bytearray and saves to self.output and calls export function

        try:
            pickle_tree = dumps(self.comp_tools["tree"])
            len_tree = len(pickle_tree).to_bytes(2, "big")
            self.output = len_tree + pickle_tree + byte_convert
        except OverflowError:
            raise OverflowError("Could not convert length of huffman tree to bytes")

        if export:  # exports created product if specified
            self.export_product(alt_out)

    def decompress(self, alt_in = None, alt_out:Path = None, export = True):

        def recursion(branch:list, section:str) -> tuple:
            """
            Recursive function to decoded characters from tree
            :param branch: slice of nested tree to be looked in
            :param section: string of 1s and 0s that is being recoded
            :return: final recursion layer returns a single character and the string
            """

            new_val = int(section[0])  # takes first "bit" from string and converts to int
            cut_down = section[1:]  # removes character from string

            # checks if new int returns character from tree
            # if it does the character is returned, if not function is recursed
            if isinstance(branch[new_val], int):
                return branch[new_val], cut_down
            else:
                return recursion(branch[new_val], cut_down)

        # if alternate worker/out file are specified, call functions to set them as main
        if alt_in:
            self.new_worker(alt_in)
        if alt_out:
            self.new_out(alt_out)

        # -------------------- #
        # gets huffman tree and compressed content from self.worker
        len_tree = int.from_bytes(self.worker[:2], "big")  # grabs first two bytes to get length of decompression tree
        decomp_tree = loads(self.worker[2:len_tree + 2])  # pulls decompress tree from file and converts to list with pickle
        padding = self.worker[len_tree + 2]  # pulls out length of bit padding for compressed string
        decomp_string = self.worker[len_tree + 3:]  # pulls compressed string

        bit_string = ""
        for num in decomp_string:  # iterates though bytes string and converts to string of 1s and 0s (ie: "10010110")
            bit_string += bin(num)[2:].zfill(8)

        bit_string = bit_string[:-padding]  # removes padding bits from end of string

        # -------------------- #
        # decompresses bit_string using huffman tree

        decoded: list[int]= []
        # while loop runs so long as characters are decode string
        while bit_string:
            char, new_work = recursion(decomp_tree, bit_string)
            decoded.append(char)  # appends found value to string
            bit_string = new_work  # assigns cut down string to decode string

        self.output = bytearray(decoded)  # converts array into bytearray and saves to self.output

        if export:  # exports created product if specified
            self.export_product(alt_out)
        

if __name__ == "__main__":
    # gets Command line arguments using argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=lambda user_path: Path(user_path), help="File to be fed into script")
    parser.add_argument("--compress", "-c", action="store_true", help="Sets script to compress passed file")
    parser.add_argument("--decompress", "-d", action="store_true", help="Sets script to decompress passed file")
    parser.add_argument("--out-file", "-o", type=lambda user_path: Path(user_path), default=None, help="(OPTIONAL) Name for output file")
    args = parser.parse_args()

    # if both decompress and compress are specified OR neither are, script exits
    if (args.compress and args.decompress) or (not args.compress and not args.decompress):
        print("Could not determine run mode for script")
        exit(1)

    worker = Huffman(args.input)
    if args.compress:
        # if no output file is given, creates one from name of input file
        auto_out = args.out_file if args.out_file else Path(args.input.stem + ".hfc") 

        print(f"Compressing file \"{args.input}\"")
        worker.compress(alt_out=auto_out)

    elif args.decompress:
        # if no output file is given, creates one from name of input file
        auto_out = args.out_file if args.out_file else Path(args.input.stem + ".txt") 

        print(f"Decompressing file \"{args.input}\"")
        worker.decompress(alt_out=auto_out)