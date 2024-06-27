import urllib.request
import json
import jwt
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

def combine_pharmacy_data():
    data_keys = [
        ('FIRST_STATUS', 'FIRST_FARMASI'),
        ('SECOND_STATUS', 'SECOND_FARMASI')
    ]

    combined_data=[]
    for first_key, second_key in data_keys:
        first_value = config[first_key]
        second_value = config[second_key]

        combined_data.extend(get_order_farmasi(first_value, second_value))
    
    return combined_data

combine_pharmacy_data()

