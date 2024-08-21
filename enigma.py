import json

class JSONFileError(Exception):
    #A custom exception for specific errors in my application.
    def __init__(self, message):
        super().__init__(message)


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
                encryption_count+=1
            else:
                result += char
            w1, w2, w3 = self.promote_wheels( w1, w2, w3,encryption_count )
        return result

    def calculate_wheels_factor(self, w1, w2, w3):
        return ((2*w1) - w2 + w3 ) % 26

    def promote_wheels(self, w1, w2, w3, encrypted_chars):
        w1 = (w1 + 1) % 9
        w2 = w2*2 if encrypted_chars % 2 == 0 else w2 -1
        w3 = 10 if encrypted_chars % 10 == 0 else 5 if encrypted_chars % 3 == 0 else 0

        return w1, w2, w3

    def calculate_encryption(self,char, w1, w2, w3):
        i = self.hash_map[char]
        wheel_factor = self.calculate_wheels_factor(w1, w2, w3)
        if wheel_factor != 0:
            i += wheel_factor
        else:
            i += 1
        i = i % 26
        c1 = find_key_by_value(self.hash_map,i)
        c2 = self.reflector_map[c1]
        i = self.hash_map[c2]
        if wheel_factor != 0:
            i -= wheel_factor
        else:
            i -=1
        i = i%26
        c3 = find_key_by_value(self.hash_map, i)
        return c3

def find_key_by_value(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key
    return None

def load_enigma_from_path(path):
    try:
        with open(path, 'r') as input_file:
            input_dictionary = json.load(input_file)
            hash_map = input_dictionary['hash_map']
            reflector_map = input_dictionary['reflector_map']
            wheels = input_dictionary['wheels']
            return Enigma(hash_map, wheels, reflector_map)
    except Exception as e:
        raise JSONFileError("The enigma script has encountered an error")

