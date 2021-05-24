import logging
logging.basicConfig(level=logging.INFO,
                    filename='auth_server.log',
                    filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

from working_module.SmartSocket import connections

import json
from working_module import request_html
from working_module import authentication

import time



with open('auth_server.pass','r') as f:
    auth_server_pass = f.readline().strip()



def get_active_product_keys() -> list:
    logging.info("function: get_active_product_keys() called")

    # setup some basic variables to track things that
    # will be needed to create the github api url
    owner = 'Machine-builder'
    repo = 'py-authentication'
    path = 'identifiers_ec.ids'

    logging.info("getting github api response")
    # request from the github api
    url = 'https://api.github.com/repos/{owner}/{repo}/contents/{path}'.format(
        owner=owner, repo=repo, path=path)
    
    logging.info('downloading file')
    resp = json.loads(request_html.request_page(url))
    download_url = resp['download_url']
    # get the actual file contents from the download_url
    content = request_html.request_page(download_url)

    # split the text up per line, to get each
    # individual machine id
    raw_product_keys = [i for i in content.split('\n') if (i and not i.startswith('//'))]

    product_keys = []
    for raw_key in raw_product_keys:
        try:
            product_keys.append(authentication.product_key(raw_key, True))
        except:
            logging.warning(f"could not load product key : {raw_key}")

    return product_keys



server_addr = (
    connections.getLocalIP(),
    13294
)

print("Starting server")
print(server_addr)

server = connections.SERVER(server_addr)
system = connections.ServerClientSystem(server)

logging.info(system.server)
logging.info(f"server address {server_addr[0]}:{server_addr[1]}")

server_running = True

while server_running:

    clients, messages, disconnected = system.main()

    admin_conns = []

    for new_client in clients:
        conn, addr = new_client
        logging.info(f"client connection from {addr[0]}:{addr[1]}")
    
    for message in messages:
        message:connections.SCS_MESSAGE = message
        if message.is_dict:
            logging.info(f"dict message {str(message.data)}, {str(message.from_conn)}")

            from_conn = message.from_conn

            active_product_keys = get_active_product_keys()

            event = message.data.get('event',None)

            if event == 'validate_key':
                # verify the provided key
                machine_key = message.data.get('key',None)
                found_key = None

                for key in active_product_keys:
                    if key.key == machine_key:
                        found_key:authentication.product_key = key
                        break
                
                if found_key is not None:
                    if found_key.is_valid():
                        response = {"validity": "valid"}
                    else:
                        response = {"validity": "invalid"}
                else:
                    response = {"validity": "unknown"}
                
                logging.info(f"send message to conn {message.from_conn} {response}")
                try:
                    system.send_to_conn(message.from_conn, response)
                except Exception as e:
                    logging.warning(f"failed to send response message {e}")
            
            elif event == 'admin_auth':
                passphrase = message.data.get('pass',None)

                if passphrase == auth_server_pass:
                    if from_conn is not None:
                        admin_conns.append(from_conn)
                    response = {"response": "success"}
                    logging.log(f"conn authorised as admin: {from_conn}")
                else:
                    response = {"response": "fail"}
                    logging.log(f"conn authorised as admin: {from_conn}")
                system.send_to_conn(from_conn, response)
            
            elif event == 'admin_ping':
                if from_conn in admin_conns:
                    response = {"response": "pong"}
                else:
                    response = {"response": "auth_needed"}
                system.send_to_conn(from_conn, response)

        else:
            logging.info(f"message is_dict:{message.is_dict}, is_pickled:{message.is_pickled}")
    
    for client in disconnected:
        client_conn = client[0]
        if client_conn in admin_conns:
            admin_conns.remove(client_conn)
        logging.info(f"client disconnected {client[1][0]}:{client[1][1]}")