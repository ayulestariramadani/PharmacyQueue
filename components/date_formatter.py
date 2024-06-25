import locale
from datetime import datetime

def date_formatter():
    # Set the locale
    try:
        locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
    except locale.Error as e:
        print(f"Error setting locale: {e}")
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    
    # Get the current date and time
    current_datetime = datetime.now()

    # Format the datetime object to the desired output format
    output_date_str = current_datetime.strftime('%A, %d %B %Y %H:%M:%S')

    return output_date_str