import json
import sys

USAGE_MESSAGE = 'Usage: python3 enigma.py -c <config_file> -i <input_file> -o <output_file>'
CONFIG_FLAG = '-c'
INPUT_FLAG = '-i'
OUTPUT_FLAG = '-o'
ERROR_MSG = "The enigma script has encountered an error"
READ_MODE = 'r'
WRITE_MODE = 'w'
HASH_MAP = "hash_map"
REFLECTOR_MAP = "reflector_map"
WHEELS ="wheels"
MIN_ARGUMENTS = 2
MAX_ARGUMENTS = 3
ENGLISH_LETTERS = 26
FIRST_WHEEL_RANGE = 8
FIRST_WHEEL_FACTOR = 2
SECOND_WHEEL_FACTOR = 2
THIRD_WHEEL_FACTOR10 = 10
THIRD_WHEEL_FACTOR5 = 5
THIRD_WHEEL_FACTOR3 = 3

class JSONFileError(Exception):
    pass


class Enigma:
    def __init__(self, hash_map, wheels, reflector_map):
            self.hash_map = hash_map
            self.reflector_map = reflector_map
            self.wheels = tuple(wheels)

    def encrypt(self, message):
        result = ""
        encryption_count = 0
        w1, w2, w3 = self.wheels
        for char in message:
            if char.isalpha() and char.islower():
                encrypted_char = self.calculate_encryption(char,w1, w2, w3)
                result+=encrypted_char
                encryption_count+=1
            else:
                result += char
            w1, w2, w3 = self.promote_wheels( w1, w2, w3,encryption_count )
        return result

    def calculate_wheels_factor(self, w1, w2, w3):
        return ((FIRST_WHEEL_FACTOR*w1) - w2 + w3 ) % ENGLISH_LETTERS

    def promote_wheels(self, w1, w2, w3, encrypted_chars):
        w1 = (w1 + 1) if w1 < FIRST_WHEEL_RANGE else 1
        w2 = w2*SECOND_WHEEL_FACTOR if encrypted_chars % SECOND_WHEEL_FACTOR == 0 else w2 -1
        w3 = THIRD_WHEEL_FACTOR10 if encrypted_chars % THIRD_WHEEL_FACTOR10 == 0 else THIRD_WHEEL_FACTOR5 if encrypted_chars % THIRD_WHEEL_FACTOR3 == 0 else 0

        return w1, w2, w3

    def calculate_encryption(self,char, w1, w2, w3):
        i = self.hash_map[char]
        wheel_factor = self.calculate_wheels_factor(w1, w2, w3)
        if wheel_factor != 0:
            i += wheel_factor
        else:
            i += 1
        i = i % ENGLISH_LETTERS
        c1 = find_key_by_value(self.hash_map,i)
        c2 = self.reflector_map[c1]
        i = self.hash_map[c2]
        if wheel_factor != 0:
            i -= wheel_factor
        else:
            i -=1
        i = i % ENGLISH_LETTERS
        c3 = find_key_by_value(self.hash_map, i)
        return c3

def find_key_by_value(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key
    return None

def load_enigma_from_path(path):
    try:
        with open(path, READ_MODE) as input_file:
            input_dictionary = json.load(input_file)
            hash_map = input_dictionary[HASH_MAP]
            reflector_map = input_dictionary[REFLECTOR_MAP]
            wheels = input_dictionary[WHEELS]
            return Enigma(hash_map, wheels, reflector_map)
    except Exception:
        raise JSONFileError(ERROR_MSG)


if __name__ == "__main__":
    try:
        args = sys.argv[1:]
        expected_flags = [CONFIG_FLAG, INPUT_FLAG, OUTPUT_FLAG]
        parsed_args = {}

        if len(args[::2]) < MIN_ARGUMENTS or len(args[::2]) > MAX_ARGUMENTS:
            print(USAGE_MESSAGE, file = sys.stderr)
            exit(1)

        i = 0
        while(i < len(args)):
            if not args[i] in expected_flags:
                print(USAGE_MESSAGE, file = sys.stderr)
                exit(1)
            elif i+1 >= len(args):
                print(USAGE_MESSAGE, file = sys.stderr)
                exit(1)
            else:
                parsed_args[args[i]] = args[i + 1]
                i += 1
            i += 1

        if not CONFIG_FLAG in parsed_args or not INPUT_FLAG in parsed_args:
            print(USAGE_MESSAGE, file=sys.stderr)
            exit(1)

        enigma = load_enigma_from_path(parsed_args[CONFIG_FLAG])

        with open(parsed_args[INPUT_FLAG], READ_MODE) as input_file:
            result = ""
            for message in input_file:
                encrypted_message = enigma.encrypt(message)
                result += encrypted_message


        if OUTPUT_FLAG in parsed_args:
            with open(parsed_args[OUTPUT_FLAG], WRITE_MODE) as output_file:
                output_file.write(result)
        else:
            print(result)

    except Exception:
        print(ERROR_MSG)
        exit(1)