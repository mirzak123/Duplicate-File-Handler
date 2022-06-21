import sys
import os
import hashlib
import re
from collections import defaultdict


class DuplicateFileHandler:
    """ Handle all files of specified type on a given path and sort them by size, hash value; and delete duplicate files
        if you so choose to.l

    - Create an instance and invoke self.start_file_handler() to get started.

    Instance variables:
        1. root_path -> stores root path in which to look for files of specified type
        2. files -> dictionary that stores lists of files with byte sizes as keys
        3. files_by_hash_value -> dictionary that stores byte sizes as keys and another dictionary as value
           that stores lists of files under the hash value of their contents
        4. duplicate_files_dict -> same structure as self.files_by_hash_value, but includes only files hash values that
           store more than one file (meaning they are duplicates)
        5. duplicate_files -> list of files containing all duplicates from self.duplicate_files_dict used for the
           purpose of deleting files by index
    """

    def __init__(self, path):
        self.root_path = path
        self.files = defaultdict(list)
        self.files_by_hash_value = dict()
        self.duplicate_files_dict = dict()
        self.duplicate_files = list()

    @staticmethod
    def prompt_user(message, option_1, option_2):
        """ Return bool value corresponding to one of two options prompted to a user regarding a message/question. """
        try:
            return {option_1: True, option_2: False}[input(message)]
        except KeyError:
            # Ask user recursively until they give an answer that corresponds to one of the two options
            print('\nWrong option\n')
            return DuplicateFileHandler.prompt_user(message, option_1, option_2)

    def start_file_handler(self):
        """ Run all capabilities of the DuplicateFileHandler in correct order. """

        file_format = input("Enter file format:\n")

        # the order of function calls below is very important!
        self.add_files(file_format)
        self.add_files_by_hash_value()
        self.add_duplicate_files()

        sorting = DuplicateFileHandler.prompt_user("\nSize sorting options:\n1. Descending\n2. Ascending\n\nEnter a "
                                                   "sorting option:\n", '1', '2')
        self.output_files(sorting)

        delete = DuplicateFileHandler.prompt_user("\nCheck for duplicates?\n", 'yes', 'no')
        self.output_duplicates(sorting)

        if delete:
            while True:
                file_numbers = input("Enter file numbers to delete:\n")
                # making sure there are no non digit characters in input
                if re.fullmatch(r'[\s\d]+', file_numbers):
                    break
                print("\nWrong format\n")  # user has entered either a letter or a floating number in one of the file nums
            file_numbers = list(map(int, file_numbers.split()))
            self.delete_files(*file_numbers)

    def add_files(self, file_format):
        """ Add all files with extension given as argument file_format to self.files using os.walk(...). If file_format
            is an empty string, self.files will contain files of all types."""

        for root, dirs, files in os.walk(self.root_path, topdown=False):
            for file in files:
                if file.endswith(file_format):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    self.files[file_size].append(file_path)

    def add_files_by_hash_value(self):
        for size, files in self.files.items():
            hash_dict = defaultdict(list)  # dictionary that will be stores as value for the current size(in bytes)
            for file in files:
                with open(file, 'rb') as f:  # hash object must get string in terms of bytes, hence 'rb'
                    content = f.read()
                # create a hash object -> update it with a string -> get hash value from it by calling .hexdigest()
                hash_obj = hashlib.md5()
                hash_obj.update(content)
                hash_value = hash_obj.hexdigest()

                hash_dict[hash_value].append(file)

            self.files_by_hash_value[size] = hash_dict

    def add_duplicate_files(self):
        """Add only duplicate files to self.duplicate_files_dict by checking the length of list under each hash value"""

        for size, hash_dict in self.files_by_hash_value.items():
            duplicate_hash_dict = dict()
            for hash_value, files in hash_dict.items():
                if len(files) > 1:
                    duplicate_hash_dict[hash_value] = files
            if duplicate_hash_dict:
                self.duplicate_files_dict[size] = duplicate_hash_dict

    def output_files(self, reverse=False):
        """ Print files under each byte size in ascending/descending order as specified by the user. """

        for size in sorted(self.files, reverse=reverse):
            files = self.files[size]
            print(f"\n{size} bytes")
            print(*files, sep='\n')
            print()

    def output_duplicates(self, reverse=False):
        """ Print contents of self.duplicate_files_dict along with a file number, as well as append those duplicates to
            self.duplicate_files in case user wants to delete them later. """

        index = 1  # file number that will increment with each output of a file
        for size, hash_dict in sorted(self.duplicate_files_dict.items(), reverse=reverse):
            print(f"\n{size} bytes")
            for hash_value, files in hash_dict.items():
                print(f"Hash: {hash_value}")
                for file in files:
                    print(f"{index}. {file}")  # will be useful for deleting files using this index
                    index += 1
                    self.duplicate_files.append(file)
                print()

    def delete_files(self, *file_numbers):
        """ Delete duplicate files that user specified using their file numbers (order in which they appeared in
            self.output_duplicates). """

        total_size = 0  # Amount of freed up space in bytes
        for num in file_numbers:
            try:
                file = self.duplicate_files[num - 1]
            except IndexError:
                # if file_number is out of range just continue
                continue
            size = os.path.getsize(file)
            os.remove(file)
            total_size += size

        print(f"\nTotal freed up space: {total_size} bytes")


def main():
    try:
        directory = sys.argv[1]
    except IndexError:
        print("Directory is not specified")
    else:
        duplicate_file_handler = DuplicateFileHandler(directory)
        duplicate_file_handler.start_file_handler()


if __name__ == '__main__':
    main()
