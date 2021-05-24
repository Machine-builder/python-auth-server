import logging
logging.basicConfig(level=logging.INFO,
                    filename='app.log',
                    filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

import json
import subprocess
import time
import uuid

from . import encryption, request_html

from .SmartSocket import connections


class second_times:
    minute = 60
    hour = 3600
    day = 86400
    week = 604800

class unique_pc_identifier(object):
    def __init__(self):
        """
        A class used to generate a unique ID
        for any given pc.

        simply access the unique_id attribute
        for access to the machine's identifier
        """
        logging.info('class init: unique_pc_identifier')

        # use subprocess to check the wmic command output, and get the uuid
        wmic_id:str = subprocess.check_output('wmic csproduct get uuid')
        wmic_id = wmic_id.decode().split('\n')[1].strip()
        # use uuid.getnode() to get another unique pc identifier, which we
        # can then combine into an even safer pc id
        uuid_id:str = str(uuid.getnode())
        # combine the previous two ids into one larger, safer id
        self.unique_id = (wmic_id+uuid_id).replace(
        '-','').replace('_','')

        logging.info(f'instance.unique_id = ...')
    
    def __repr__(self):
        # just so print() works for class instances
        return f'unique_pc_identifier<{self.unique_id}>'

class unique_key(object):
    def __init__(self) -> None:
        u_id = unique_pc_identifier().unique_id
        self.key = encryption.encrypt_str(u_id)


class product_key(object):
    def __init__(self, input_data, encrypted:bool=False) -> None:
        if encrypted:
            # decrypt the input_data
            decrypted_str = encryption.decrypt_str(input_data)
            decoded_json = json.loads(decrypted_str)
            input_data = decoded_json
        
        self.key = input_data['key']
        self.valid_until = input_data['valid_until']
        self.created_at = input_data.get('created_at', time.time())

    @staticmethod
    def get_personal_key(last_for:int=second_times.week*2):
        """defaults to last for 2 weeks"""
        return product_key({
            "key": unique_key().key,
            "valid_until": time.time()+last_for,
            "created_at": time.time()
        })
    
    def as_json(self):
        return {
            "key": self.key,
            "valid_until": self.valid_until,
            "created_at": self.created_at
        }
    
    def is_valid(self) -> bool:
        if self.valid_until == -1: return True
        return self.valid_until > time.time()


def is_system_valid():
    logging.info("function: is_system_valid() called")

    machine_key = unique_key().key

    logging.info("initialise tcp client")
    client = connections.SCS_CLIENT()

    server_ip = "192.168.15.17"
    server_port = 13294

    logging.info(f"connect to server: {server_ip}:{server_port}")
    client.connect((server_ip, server_port))

    send_data = {
        'event': 'validate_key',
        'key': machine_key
    }
    client.hsend_o(send_data)

    recv_resp = False
    while not recv_resp:
        messages, _ = client.get_new_messages(True,True)

        if len(messages) > 0:
            recv_resp = True

    response = messages[0].data
    print(response)

    client.conn.close()
        