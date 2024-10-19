# auto_hosts.py
# Automatically generate a /etc/hosts file for your Pi-hole based on all current MAC address connections.
#
# Visit site below and sign up for API key
# https://macaddress.io/api
#
# You will get this error if you run out of credits:
# 100 FREE requests daily. No credit card required.
# maclookup.exceptions.not_enough_credits_exception.NotEnoughCreditsException
# urllib.error.HTTPError: HTTP Error 402: Payment Required

# import libraries
import pandas as pd
import os
from maclookup import ApiClient
import logging
import time
import ast

# Set the variable in the Python environment
os.environ['MY_VARIABLE'] = 'Hello World'
# Replace                xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx with your key from macaddress.io/api
os.environ['API_KEY'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
os.environ['LOG_FILENAME'] = 'myapp.log'
os.environ['OUTPUT_FILENAME'] = 'result.csv'

# Export the variable to the shell
os.system('export MY_VARIABLE')
os.system('export API_KEY')
os.system('export LOG_FILENAME')
os.system('export OUTPUT_FILENAME')

# Use arp -n to record network devices into a database file
os.system('clear')
os.system('arp -n > hosts0.txt')

# Read in the database of network devices
df = pd.read_csv('hosts0.txt', delimiter='\s+')
print('df= Results of apr -n')
print(df)

# Clean data
df1 = df.drop(['HWtype', 'Flags', 'Mask', 'Iface'], axis=1)
print('df1')
print(df1.to_markdown())
df2 = df1[df1.HWaddress != "eth0"]

# Reset the index
df2 = df2.reset_index(drop=True)
print('df2')
print(df2.to_markdown())

# Create a new column to store hardware vendor information
df2['HardwareVendor'] = "None"
print('df2')
print(df2.to_markdown())
# print(df2.dtypes)

# Iterate over all rows and populate the hardware_vendor column
for index, row in df2.iterrows():
    mac_address = row['HWaddress']  # Assuming 'HWaddress' is the column with MAC addresses
    # Decode hardware vendor
    api_key = os.environ['API_KEY']
    log_file = os.environ['LOG_FILENAME']

    client = ApiClient(api_key)

    logging.basicConfig(filename=log_file, level=logging.WARNING)
    
    # Use a timer to defeat rate limiting
    # print("Starting timer to defeat rate limiting...")
    time.sleep(0.1)  # Wait for 0.1 seconds

    # Attempt to get vendor information
    try:
        df2.at[index, 'HardwareVendor'] = client.get_vendor(mac_address) or "Unknown Vendor"
        print('Decoding...')        
        print(mac_address)
        # print(client.get_vendor(mac_address))
    except maclookup.exceptions.invalid_mac_or_oui_exception.InvalidMacOrOuiException:  # Use the full exception name
        df2.at[index, 'HardwareVendor'] = "Invalid MAC Address"
    except Exception as e:  # Catch other potential exceptions (optional)
        logging.warning("Error looking up MAC address {mac_address}: {e}")
        df2.at[index, 'HardwareVendor'] = "Lookup Failed"

# Get rid of all the 'b & '
print('df2 after decoding')
print(df2.to_markdown())

# Store the results again
print("Writing to file...")
df2.to_csv('hosts1.txt', sep='\t', index=True)

# Replace 'your_file.txt' with the actual path to your file
file_path = 'hosts1.txt'

# If your file is delimited by something other than a comma, specify the delimiter
df3 = pd.read_csv(file_path, sep='\t')
print(df3)

# This is not necasarry but didn't want to renumber below
df4 = df3

df5 = df4
df5['HardwareVendor'] = df5['HardwareVendor'].str.replace("b'", "", regex=True)
print('df5')
print(df5.to_markdown())

df6 = df5
df6['HardwareVendor'] = df6['HardwareVendor'].str.replace("'", "", regex=True)
print('df6')
print(df6.to_markdown())

df7 = df6
df7['HardwareVendor'] = df7['HardwareVendor'].str.replace(" ", "", regex=True)
print('df7')
print(df7.to_markdown())

df8 = df7
df8['HardwareVendor'] = df8['HardwareVendor'].str.replace(",", "", regex=True)
print('df8')
print(df8.to_markdown())

df9 = df8
df9['HardwareVendor'] = df9['HardwareVendor'].str.replace("(", "", regex=True)
print('df9')
print(df9.to_markdown())

df10 = df9
df10['HardwareVendor'] = df10['HardwareVendor'].str.replace(")", "", regex=True)
print('df10')

df11 = df10
df11['HardwareVendor'] = df11['HardwareVendor'].str.replace("-", "", regex=True)
print('df11')
print(df11.to_markdown())

# Store the results again
print("Writing to file...")
df11.to_csv('hosts2.txt', sep='\t', index=False)

# Store the results in format /etc/hosts file for pihole will accept
df12 = df11
df12 = df12[['Address', 'HardwareVendor']]
print("Writing to file...")
df12.to_csv('hosts3.txt', sep='\t', index=False, header=False)

print("Copy contents of hosts3.txt to your /etc/hosts file.")
