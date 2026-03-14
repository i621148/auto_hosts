# auto_hosts.py
# Automatically generate a /etc/hosts file for your Pi-hole based on all current MAC address connections.
#
# Visit site below and sign up for API key
# https://macaddress.io/api

import pandas as pd
import os
from maclookup import ApiClient
import maclookup.exceptions
import logging
import time

# --- Configuration ---
# Replace the x's below with your actual API key from macaddress.io/api
os.environ['API_KEY'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
os.environ['LOG_FILENAME'] = 'myapp.log'

# Use arp -n to record network devices into a text file
print("Grabbing ARP table...")
os.system('arp -n > hosts0.txt')

# Read in the database of network devices
# (Using r'\s+' to prevent pandas deprecation warnings)
df = pd.read_csv('hosts0.txt', delimiter=r'\s+')
print('\n--- Results of arp -n ---')
print(df)

# Clean data: Drop unnecessary columns and the router/interface itself (eth0)
df_clean = df.drop(['HWtype', 'Flags', 'Mask', 'Iface'], axis=1)
df_clean = df_clean[df_clean.HWaddress != "eth0"]
df_clean = df_clean.reset_index(drop=True)

# Create a new column to store hardware vendor information
df_clean['HardwareVendor'] = "None"

print('\n--- Starting MAC address lookups ---')
api_key = os.environ['API_KEY']
log_file = os.environ['LOG_FILENAME']
client = ApiClient(api_key)
logging.basicConfig(filename=log_file, level=logging.WARNING)

# Iterate over all rows and populate the HardwareVendor column
for index, row in df_clean.iterrows():
    mac_address = row['HWaddress']
    
    # Use a timer to defeat rate limiting
    time.sleep(0.1) 

    # Attempt to get vendor information
    try:
        vendor = client.get_vendor(mac_address) or "UnknownVendor"
        df_clean.at[index, 'HardwareVendor'] = str(vendor)
        print(f"Decoding {mac_address} -> {vendor}")
    except maclookup.exceptions.invalid_mac_or_oui_exception.InvalidMacOrOuiException:
        df_clean.at[index, 'HardwareVendor'] = "InvalidMACAddress"
        print(f"Decoding {mac_address} -> Invalid MAC")
    except Exception as e:
        logging.warning(f"Error looking up MAC address {mac_address}: {e}")
        df_clean.at[index, 'HardwareVendor'] = "LookupFailed"
        print(f"Decoding {mac_address} -> Lookup Failed")

# Save intermediate results (Optional, left in for your debugging)
df_clean.to_csv('hosts1.txt', sep='\t', index=True)

print('\n--- Cleaning up vendor strings ---')
# Chain all the string replacements together to remove b'', spaces, commas, and parentheses.
# regex=False prevents the "unterminated subpattern" crash!
df_clean['HardwareVendor'] = (
    df_clean['HardwareVendor']
    .str.replace("b'", "", regex=False)
    .str.replace("'", "", regex=False)
    .str.replace(" ", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.replace("(", "", regex=False)
    .str.replace(")", "", regex=False)
    .str.replace("-", "", regex=False)
)

print(df_clean.to_markdown())

# Save cleaned intermediate file
df_clean.to_csv('hosts2.txt', sep='\t', index=False)

# Format specifically for /etc/hosts (Address and HardwareVendor only)
df_final = df_clean[['Address', 'HardwareVendor']]
print("\nWriting final output to hosts3.txt...")
df_final.to_csv('hosts3.txt', sep='\t', index=False, header=False)

print("\nDONE! Copy the contents of hosts3.txt to your /etc/hosts file.")