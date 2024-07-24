import urllib.request
import json
from datetime import datetime
from dotenv import dotenv_values
import logging

config = dotenv_values(".env")
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()])
current_date = datetime.now().date()

def login_sso():
    # Define the data to be sent in the POST request
    data = {
        "LOGIN": config['LOGIN'],
        "PASSWORD": config['PASSWORD']
    }
    url = config['URL_SSO']

    # Define the headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Convert the data to a JSON string and then to bytes
    data = json.dumps(data).encode('utf-8')
    # Create a request object
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')

    # Make the request
    try:
        with urllib.request.urlopen(req) as response:
            # Read the response
            response_data = response.read()
            # Decode the response to a string
            response_data = response_data.decode('utf-8')
            # Parse the string to a JSON object
            json_response = json.loads(response_data)
            # logging.error the parsed JSON data
            jwt_token_sso = json_response['data']['jwt_token']
            return jwt_token_sso
            

    except urllib.error.URLError as e:
        logging.error(f'Error login sso: {e.reason}')
        return None
    

def new_token_simata():
    url = config['URL_SIMATA']
    token = login_sso()
    headers = {
            'Authorization': f'Bearer {token}',  # Replace with your Bearer token
            'Content-Type': 'application/json'  # If you are sending JSON data
    }

    req = urllib.request.Request(url, headers=headers, method='GET')

    # Make the request
    try:
        with urllib.request.urlopen(req) as response:
            # Read the response
            response_data = response.read()
            # Decode the response to a string
            response_data = response_data.decode('utf-8')
            # Parse the string to a JSON object
            json_response = json.loads(response_data)
            # logging.error the parsed JSON data
            jwt_token = json_response['data']['jwt_token']
            # return jwt_token
            return jwt_token

    except urllib.error.URLError as e:
        logging.error(f'Error new token: {e.reason}')
        return None

def get_order_farmasi(status_code, farmasi_code):
    url = config['URL_ORDER_FARMASI']
    token = new_token_simata()

    # Get the current date
    # current_date = datetime.now().date()

    data = {
        'PNOPEN': '',
        'PTANGGAL': f"{current_date}",
        'PNORM': '',
        'PTUJUAN': '',
        'PSTATUS': status_code,
        'PFARMASI': farmasi_code,
    }
    # Convert the data to a JSON string and then to bytes
    data = json.dumps(data).encode('utf-8')

    headers = {
            'Authorization': f'Bearer {token}',  # Replace with your Bearer token
            'Content-Type': 'application/json'  # If you are sending JSON data
    }

    req = urllib.request.Request(url, data=data, headers=headers, method='POST')

    # Make the request
    try:
        with urllib.request.urlopen(req) as response:
            # Read the response
            response_data = response.read()
            # Decode the response to a string
            response_data = response_data.decode('utf-8')
            # Parse the string to a JSON object
            json_response = json.loads(response_data)
            # logging.error the parsed JSON data
            pharmacy_data = json_response.get('data', [])
            if not pharmacy_data:
                return []
            return pharmacy_data

    except urllib.error.URLError as e:
        logging.error(f'Error get order farmasi: {e.reason}')
        return None

def get_order_refraksi():
    url = config['URL_ORDER_REFRAKSI']
    token = new_token_simata()

    # Get the current date
    # current_date = datetime.now().date()
    # current_date = '2024-06-25'

    data = {
        'PNOPEN': '',
        'PTANGGAL': f"{current_date}",
        'PDOKTER' : '',
        'PSTATUS': '',
    }
    # Convert the data to a JSON string and then to bytes
    data = json.dumps(data).encode('utf-8')

    headers = {
            'Authorization': f'Bearer {token}',  # Replace with your Bearer token
            'Content-Type': 'application/json'  # If you are sending JSON data
    }

    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    # Make the request
    try:
        with urllib.request.urlopen(req) as response:
            # Read the response
            response_data = response.read()
            # Decode the response to a string
            response_data = response_data.decode('utf-8')
            # Parse the string to a JSON object
            json_response = json.loads(response_data)
            # logging.error the parsed JSON data
            refraction_data = json_response.get('data', [])
            if not refraction_data:
                return []
            return refraction_data

    except urllib.error.URLError as e:
        logging.error(f'Error get order refraksi: {e.reason}')
        return None

def get_antrian_farmasi():
    base_url = config['URL_GET_ANTRIAN_FARMASI']
    token = new_token_simata()

    id = '0'
    url = base_url.format(id)

    headers = {
            'Authorization': f'Bearer {token}',  # Replace with your Bearer token
            'Content-Type': 'application/json'  # If you are sending JSON data
    }

    req = urllib.request.Request(url, headers=headers, method='GET')
    # Make the request
    try:
        with urllib.request.urlopen(req) as response:
            # Read the response
            response_data = response.read()
            # Decode the response to a string
            response_data = response_data.decode('utf-8')
            # Parse the string to a JSON object
            json_response = json.loads(response_data)
            # logging.error the parsed JSON data
            antrian_farmasi = json_response.get('data', [])
            
            if antrian_farmasi is None:
                return []
            else:
                sorted_antrian = sorted(antrian_farmasi, key=lambda x: (x["IS_ACTIVE"] == 0, x["IS_ACTIVE"]))
            return sorted_antrian

    except urllib.error.URLError as e:
        logging.error(f'Error get antrian farmasi: {e.reason}')
        return None

def add_antrian_farmasi(queue, norm, nama_lengkap, dokter, asal, tanggal_order):
    url = config['URL_ADD_ANTRIAN_FARMASI']
    token = new_token_simata()

    queue = queue if queue is not None else ''
    norm = norm if norm is not None else ''
    nama_lengkap = nama_lengkap if nama_lengkap is not None else ''
    dokter = dokter if dokter is not None else ''
    asal = asal if asal is not None else ''
    tanggal_order = tanggal_order if tanggal_order is not None else ''

    data = {
        "QUEUE": queue,
        "NORM": norm,
        "NAMA_LENGKAP": nama_lengkap,
        "DOKTER": dokter,
        "ASAL_PASIEN": asal,
        "TANGGAL_ORDER": tanggal_order,
    }
    # Convert the data to a JSON string and then to bytes
    data = json.dumps(data).encode('utf-8')

    headers = {
            'Authorization': f'Bearer {token}',  # Replace with your Bearer token
            'Content-Type': 'application/json'  # If you are sending JSON data
    }

    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    # Make the request
    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            json_response = json.loads(response_data)
            if json_response.get('status') == 'success':
                logging.error('Entry added successfully')
                return json_response.get('data')
            else:
                logging.error('Failed to add entry:', json_response.get('message'))
                return None
    except Exception as e:
        logging.error(f"Error adding entry to antrian farmasi: {e}")
        return None

def update_antrian_farmasi(id, is_active):
    url = config['URL_UPDATE_ANTRIAN_FARMASI']
    token = new_token_simata()

    data = {
        "ID": id,
        "IS_ACTIVE": is_active,
    }
    # Convert the data to a JSON string and then to bytes
    data = json.dumps(data).encode('utf-8')

    headers = {
            'Authorization': f'Bearer {token}',  # Replace with your Bearer token
            'Content-Type': 'application/json'  # If you are sending JSON data
    }

    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    # Make the request
    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            json_response = json.loads(response_data)
            if json_response.get('status') == 'success':
                logging.error('Entry added successfully')
                return json_response.get('data')
            else:
                logging.error('Failed to add entry:', json_response.get('message'))
                return None
    except Exception as e:
        logging.error(f"Error adding entry to antrian farmasi: {e}")
        return None

def delete_antrian_farmasi(id):
    base_url = config['URL_DELETE_ANTRIAN_FARMASI']
    token = new_token_simata()

    url = base_url.format(id)

    headers = {
            'Authorization': f'Bearer {token}',  # Replace with your Bearer token
            'Content-Type': 'application/json'  # If you are sending JSON data
    }

    req = urllib.request.Request(url, headers=headers, method='GET')
    # Make the request
    try:
        with urllib.request.urlopen(req) as response:
            # Read the response
            response_data = response.read()
            # Decode the response to a string
            response_data = response_data.decode('utf-8')
            # Parse the string to a JSON object
            json_response = json.loads(response_data)
            # logging.error the parsed JSON data
            antrian_farmasi = json_response.get('data', [])
            if not antrian_farmasi:
                return []
            return antrian_farmasi

    except urllib.error.URLError as e:
        logging.error(f'Error delete antrian: {e.reason}')
        return None

def combine_pharmacy_data():
    data_keys = [
        ('FIRST_STATUS', 'FIRST_FARMASI'),
        ('SECOND_STATUS', 'SECOND_FARMASI')
    ]

    combined_data=[]
    antrian = get_antrian_farmasi()
    combined_data.extend(antrian)
    for first_key, second_key in data_keys:
        first_value = config[first_key]
        second_value = config[second_key]

        data = get_order_farmasi(first_value, second_value)
        try:
            combined_data.extend(data)
        except urllib.error.URLError as e:
            logging.error(f'Error combine farmasi data: {e.reason}')
            return None
    
    unique_queues = {}
    unique_data = []
    for entry in combined_data:
        queue = entry['QUEUE']
        if queue == "":
            unique_data.append(entry)
        else:
            if queue and queue not in unique_queues:
                unique_queues[queue] = entry
                unique_data.append(entry)     
    # return combined_data
    return unique_data

def combine_pharmacy_admin():
    data_keys = [
        ('FIRST_STATUS', 'FIRST_FARMASI'),
        ('SECOND_STATUS', 'SECOND_FARMASI'),
        ('THIRD_STATUS', 'THIRD_FARMASI')
    ]

    combined_data=[]
    antrian = get_antrian_farmasi()
    if antrian:
        max_antrian = max(x['IS_ACTIVE'] for x in antrian)
    else:
        max_antrian = 0
    
    combined_data.extend(antrian)
    for first_key, second_key in data_keys:
        first_value = config[first_key]
        second_value = config[second_key]

        data = get_order_farmasi(first_value, second_value)
        try:
            combined_data.extend(data)   
        except urllib.error.URLError as e:
            logging.error(f'Error farmasi admin: {e.reason}')
            return None

    unique_queues = {}
    unique_data = []
    for entry in combined_data:
        queue = entry['QUEUE']
        if queue == "":
            unique_data.append(entry)
        else:
            if queue and queue not in unique_queues:
                unique_queues[queue] = entry
                unique_data.append(entry) 

            if 'STATUS_ORDER_RESEP' in entry:
                if entry['STATUS_FARMASI'] == '1' and entry['STATUS_ORDER_RESEP'] == '2':
                    found = any(pasien['QUEUE'] == queue for pasien in antrian )
                    if not found:
                        add_antrian_farmasi(entry['QUEUE'], entry['NORM'], entry['NAMA_LENGKAP'], entry['DOKTER'], entry['ASAL_PASIEN'], entry['TANGGAL_ORDER'])
                    

    # return combined_data
    return unique_data, max_antrian

def delete_prev_date_data():
    antrian = get_antrian_farmasi()
    current_date_str = current_date.strftime('%Y-%m-%d')
    for data in antrian:
        if data['TANGGAL_ORDER']!=current_date_str:
            delete_antrian_farmasi(id=data['ID'])


