import urllib.request
import json
from datetime import datetime
from dotenv import dotenv_values

config = dotenv_values(".env")

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
            # Print the parsed JSON data
            jwt_token_sso = json_response['data']['jwt_token']
            return jwt_token_sso
            

    except urllib.error.URLError as e:
        print(f'Error: {e.reason}')
    

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
            # Print the parsed JSON data
            jwt_token = json_response['data']['jwt_token']
            # return jwt_token
            return jwt_token

    except urllib.error.URLError as e:
        print(f'Error: {e.reason}')

def get_order_farmasi(status_code, farmasi_code):
    url = config['URL_ORDER_FARMASI']
    token = new_token_simata()

    # Get the current date
    current_date = datetime.now().date()

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
            # Print the parsed JSON data
            pharmacy_data = json_response.get('data', [])
            if not pharmacy_data:
                return []
            return pharmacy_data

    except urllib.error.URLError as e:
        print(f'Error: {e.reason}')

def get_order_refraksi():
    url = config['URL_ORDER_REFRAKSI']
    token = new_token_simata()

    # Get the current date
    current_date = datetime.now().date()
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
            # Print the parsed JSON data
            refraction_data = json_response.get('data', [])
            print(refraction_data)
            if not refraction_data:
                return []
            return refraction_data

    except urllib.error.URLError as e:
        print(f'Error: {e.reason}')

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
            # Print the parsed JSON data
            antrian_farmasi = json_response.get('data', [])
            if not antrian_farmasi:
                return []
            return antrian_farmasi

    except urllib.error.URLError as e:
        print(f'Error: {e.reason}')

def add_antrian_farmasi(status_antrian, norm, nama_lengkap, dokter, asal):
    url = config['URL_ADD_ANTRIAN_FARMASI']
    token = new_token_simata()

    status_antrian = status_antrian if status_antrian is not None else ''
    norm = norm if norm is not None else ''
    nama_lengkap = nama_lengkap if nama_lengkap is not None else ''
    dokter = dokter if dokter is not None else ''
    asal = asal if asal is not None else ''

    data = {
        "QUEUE": status_antrian,
        "NORM": norm,
        "NAMA_LENGKAP": nama_lengkap,
        "DOKTER": dokter,
        "ASAL_PASIEN": asal,
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
                print('Entry added successfully')
                return json_response.get('data')
            else:
                print('Failed to add entry:', json_response.get('message'))
                return None
    except Exception as e:
        print(f"Error adding entry to antrian farmasi: {e}")
        return None

def delete_antrian_farmasi(id):
    base_url = config['URL_DELETE_ANTRIAN_FARMASI']
    token = new_token_simata()

    url = base_url.format(id)
    print(id)

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
            # Print the parsed JSON data
            antrian_farmasi = json_response.get('data', [])
            if not antrian_farmasi:
                return []
            return antrian_farmasi

    except urllib.error.URLError as e:
        print(f'Error: {e.reason}')

def combine_pharmacy_data():
    data_keys = [
        ('FIRST_STATUS', 'FIRST_FARMASI'),
        ('SECOND_STATUS', 'SECOND_FARMASI')
    ]

    combined_data=[]
    combined_data.extend(get_antrian_farmasi())
    for first_key, second_key in data_keys:
        first_value = config[first_key]
        second_value = config[second_key]

        data = get_order_farmasi(first_value, second_value)
        try:
            combined_data.extend(data)
        except urllib.error.URLError as e:
            print(f'Error: {e.reason}')
    
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
    
    combined_data.extend(get_antrian_farmasi())
    for first_key, second_key in data_keys:
        first_value = config[first_key]
        second_value = config[second_key]

        data = get_order_farmasi(first_value, second_value)
        try:
            combined_data.extend(data)   
        except urllib.error.URLError as e:
            print(f'Error: {e.reason}')

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

combine_pharmacy_data()

