import base64
import json
import os
import platform
import re
from pycurl import Curl
import logging
from io import BytesIO as StringIO
logging.getLogger(__name__)


def get_chain_config_params():
    operating_system = platform.system()
    ac_dir = ''
    if operating_system == 'Darwin':
        ac_dir = os.environ['HOME'] + '/Library/Application Support/Komodo/MCL'
    elif operating_system == 'Linux':
        ac_dir = os.environ['HOME'] + '/.komodo/MCL'
    elif operating_system == 'Win64' or operating_system == 'Windows':
        ac_dir = '%s/komodo/MCL' % os.environ['APPDATA']
    coin_config_file = str(ac_dir + '/' + 'MCL.conf')
    with open(coin_config_file, 'r') as conf_file:
        for line in conf_file:
            if re.search('rpcuser', line.rstrip()):
                rpcuser = line.rstrip().replace('rpcuser=', '')
            elif re.search('rpcpassword', line.rstrip()):
                rpcpassword = line.rstrip().replace('rpcpassword=', '')
            elif re.search('rpcport', line.rstrip()):
                rpcport = line.rstrip().replace('rpcport=', '')
    return {'rpcuser': rpcuser, 'rpcpassword': rpcpassword, 'rpcport': rpcport}

# def curl_debug_log(debug_type, debug_msg):
#     logging.debug("debug(%d): %s" % (debug_type, debug_msg.decode('utf8')))

def curl_connection():
    config_params = get_chain_config_params()
    curl = Curl()
    curl.setopt(curl.URL, 'http://127.0.0.1:%s' % config_params['rpcport'])
    b64cred = base64.b64encode(('%s:%s' % (config_params['rpcuser'], config_params['rpcpassword'])).encode('utf8'))
    curl.setopt(curl.HTTPHEADER, ["Content-Type: text/plain", "Authorization: Basic {}".format(b64cred.decode('utf8'))])
    # curl.setopt(curl.VERBOSE, True)  # to print entire request flow
    # curl.setopt(curl.DEBUGFUNCTION, curl_debug_log)
    return curl


def curl_response(method, params):
    curl_cnn = curl_connection()
    response = StringIO()
    body_as_dict = {"jsonrpc": "2.0", "id": "curl", "method": method, "params": params}
    body_as_json_string = json.dumps(body_as_dict)  # dict to json
    curl_cnn.setopt(curl_cnn.WRITEFUNCTION, response.write)
    curl_cnn.setopt(curl_cnn.POSTFIELDS, body_as_json_string)
    curl_cnn.perform()
    status_code = curl_cnn.getinfo(curl_cnn.RESPONSE_CODE)
    response = json.loads(response.getvalue())
    curl_cnn.close()
    out = response.get('result')
    if out:
        out = json.dumps(out)
    err = response.get('error')
    if err:
        err = json.dumps(err)
    return out, err, status_code
