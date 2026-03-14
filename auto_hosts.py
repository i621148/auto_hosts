# auto_hosts.py
# Automatically generate a /etc/hosts file for your Pi-hole based on all current MAC address connections.
# Refactored to use local in-memory processing and a local MAC OUI database.

import pandas as pd
import subprocess
import io
from mac_vendor_lookup import MacLookup

# --- Configuration ---
# Name of the final output file
OUTPUT_FILE = 'hosts_pihole.txt'

print("Grabbing ARP table directly into memory...")
# Run the 'arp -n' command and capture the output directly into a Python variable
arp_process = subprocess.run(['arp', '-n'], capture_output=True, text=True)
arp_data = arp_process.stdout

# Read the in-memory string into a Pandas DataFrame
# (Using r'\s+' to handle variable amounts of whitespace between columns)
df = pd.read_csv(io.StringIO(arp_data), delimiter=r'\s+')
print('\n--- Raw ARP Data ---')
print(df)

# Clean data: Drop unnecessary columns and the router/interface itself (eth0)
# errors='ignore' ensures it won't crash if your specific Linux distro names a column slightly differently
df_clean = df.drop(['HWtype', 'Flags', 'Mask', 'Iface'], axis=1, errors='ignore')
df_clean = df_clean[df_clean.HWaddress != "eth0"]
df_clean = df_clean.reset_index(drop=True)

# Create a new column to store hardware vendor information
df_clean['HardwareVendor'] = "None"

print('\n--- Initializing Local MAC Database ---')
mac_db = MacLookup()
# This downloads/updates the latest global MAC registry from the IEEE directly to your Pi.
# It only takes a few seconds and requires no API key.
mac_db.update_vendors() 

print('\n--- Starting Local MAC address lookups ---')
# Iterate over all rows and populate the HardwareVendor column
for index, row in df_clean.iterrows():
    mac_address = row['HWaddress']
    
    # Attempt to get vendor information locally (No time.sleep needed!)
    try:
        vendor = mac_db.lookup(mac_address)
        df_clean.at[index, 'HardwareVendor'] = str(vendor)
        print(f"Decoding {mac_address} -> {vendor}")
    except Exception:
        # If the MAC address isn't in the global database, it will throw an exception
        df_clean.at[index, 'HardwareVendor'] = "UnknownVendor"
        print(f"Decoding {mac_address} -> Unknown Vendor")

print('\n--- Cleaning up vendor strings ---')
# Chain all the string replacements together to remove punctuation and spaces
# regex=False prevents regular expression errors
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

# Format specifically for /etc/hosts (Address and HardwareVendor only)
df_final = df_clean[['Address', 'HardwareVendor']]

print(f"\nWriting final output to {OUTPUT_FILE}...")
# We only write to the hard drive once at the very end!
df_final.to_csv(OUTPUT_FILE, sep='\t', index=False, header=False)

print(f"\nDONE! Copy the contents of {OUTPUT_FILE} to your /etc/hosts file.")