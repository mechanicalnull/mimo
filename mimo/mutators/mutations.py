import random
import string

basic_ascii = string.ascii_letters + string.punctuation + ' '

def flip_one_bit(b: bytearray, byte_index: int, bit_index: int) -> bytearray:
    b[byte_index] = b[byte_index] ^ (1 << bit_index)
    return b

def flip_random_bit(b: bytearray) -> bytearray:
    bit_number = random.randint(0, len(b) * 8 - 1)
    byte_index = bit_number // 8
    bit_index = bit_number % 8
    return flip_one_bit(b, byte_index, bit_index)

def set_random_byte(b: bytearray) -> bytearray:
    index = random.randint(0, len(b)-1)
    value = random.randint(0, 255)
    # Don't waste time if it's not different
    while value == b[index]:
        value = random.randint(0, 255)
    b[index] = value
    return b

def set_random_ascii(b: bytearray, charset: str=basic_ascii) -> bytearray:
    index = random.randint(0, len(b)-1)
    value = random.choice(charset)
    # Don't waste time if it's not different
    while value == b[index]:
        value = random.choice(charset)
    b[index] = ord(value)
    return b

def set_random_letter(b: bytearray) -> bytearray:
    return set_random_ascii(b, string.ascii_letters)

def set_random_uppercase(b: bytearray) -> bytearray:
    return set_random_ascii(b, string.ascii_uppercase)