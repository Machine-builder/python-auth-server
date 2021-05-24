import base64
import string
import logging


possible_letters = string.ascii_letters+string.digits+'='
def caesar_encryption(input_str:str, key:int) -> str:
    """Take an input string and apply the
    caesar encryption algorithm to it"""
    logging.info(f"FUNCTION_CALLED caesar_encryption({input_str}, {key})")

    direction = 1 if key > 0 else -1

    outstr = ''
    for char in input_str:
        if char in possible_letters:
            index = possible_letters.index(char)
            index += key
            new_index = index%len(possible_letters)
            outstr += possible_letters[new_index]
            key += direction
        else:
            logging.warning(f"{char} not in possible_letters")
    
    return outstr


def base64_process(input_str:str, encode:bool=True):
    """Encode or decode a base64 string"""
    logging.info(f"FUNCTION_CALLED base64_process({input_str}, {encode})")

    if encode: return base64.b64encode(input_str.encode('ascii')).decode('ascii')
    return base64.b64decode(input_str.encode('ascii')).decode('ascii')


def encrypt_str(input_str:str) -> str:
    """Encrypts using caesar_encryption & base64"""
    logging.info(f"FUNCTION_CALLED encrypt_str({input_str})")

    step_1 = base64_process(input_str, True)
    step_2 = caesar_encryption(step_1, 5)
    return step_2


def decrypt_str(input_str:str) -> str:
    """Decrypts using caesar_encryption & base64"""
    logging.info(f"FUNCTION_CALLED decrypt_str({input_str})")

    step_1 = caesar_encryption(input_str, -5)
    step_2 = base64_process(step_1, False)
    return step_2


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        filename='app.log',
                        filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')
    
    message = 'this string can be whatever... it does not matter.'

    e = encrypt_str(message)
    print(e)

    print(decrypt_str(e))