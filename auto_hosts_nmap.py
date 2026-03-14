# auto_hosts.py
# Generates a /etc/hosts file using local MAC lookups, a custom vendor dictionary, 
# and active network fingerprinting for unknown devices.

import pandas as pd
import subprocess
import io
import socket
import nmap
import re
from mac_vendor_lookup import MacLookup

# --- Configuration ---
OUTPUT_FILE = 'hosts_pihole.txt'

# SOLUTION 1: The "Good Enough" Dictionary
# Map your cleaned vendor names to friendly device categories
DEVICE_DICTIONARY = {
    'WyzeLabsInc': 'WyzeCam',
    'SynologyIncorporated': 'SynologyNAS',
    'AppleInc': 'AppleDevice',
    'CANONINC': 'CanonPrinter',
    'TPLINKTECHNOLOGIESCOLTD': 'TPLink-SmartDevice',
    'TPLinkSystemsInc': 'TPLink-SmartDevice',
    'SkyBellTechnologiesInc': 'SkyBell-Doorbell',
    'VantivaTechnologiesBelgium': 'Vantiva-Router',
    'AlphaNetworksInc': 'Alpha-Device',
    'IEEERegistrationAuthority': 'Generic-IEEE'
}

print("Grabbing ARP table directly into memory...")
arp_process = subprocess.run(['arp', '-n'], capture_output=True, text=True)
df = pd.read_csv(io.StringIO(arp_process.stdout), delimiter=r'\s+')

# Clean initial ARP data
df_clean = df.drop(['HWtype', 'Flags', 'Mask', 'Iface'], axis=1, errors='ignore')
df_clean = df_clean[df_clean.HWaddress != "eth0"]
df_clean = df_clean.reset_index(drop=True)
df_clean['HardwareVendor'] = "UnknownVendor"
df_clean['FinalHostname'] = ""

print('\n--- Updating Local MAC Database ---')
mac_db = MacLookup()
mac_db.update_vendors() 

print('\n--- Starting MAC Lookups & Fingerprinting ---')
# Initialize Nmap scanner
nm = nmap.PortScanner()

for index, row in df_clean.iterrows():
    mac_address = row['HWaddress']
    ip_address = row['Address']
    
    # 1. MAC OUI Lookup
    try:
        raw_vendor = str(mac_db.lookup(mac_address))
    except Exception:
        raw_vendor = "UnknownVendor"
        
    # Clean the vendor string (remove spaces and punctuation)
    clean_vendor = re.sub(r'[\s\'\(\)\-\,]', '', raw_vendor).replace("b", "", 1)
    df_clean.at[index, 'HardwareVendor'] = clean_vendor

    # 2. Apply Dictionary (Solution 1)
    if clean_vendor in DEVICE_DICTIONARY:
        base_name = DEVICE_DICTIONARY[clean_vendor]
        hostname = f"{base_name}-{index}"
        print(f"[DICT MATCH] {ip_address} ({clean_vendor}) -> {hostname}")
        
    # 3. Active Fingerprinting (Solution 2 - Fallback for unknowns)
    else:
        print(f"[SCANNING] {ip_address} ({clean_vendor}) is unknown. Probing...")
        hostname = None
        
        # Try Reverse DNS (Catches mDNS/Bonjour broadcasts from IoT)
        try:
            detected_host = socket.gethostbyaddr(ip_address)[0]
            if detected_host and detected_host != ip_address:
                hostname = detected_host.split('.')[0] # e.g., 'Apple-TV.local' -> 'Apple-TV'
        except socket.herror:
            pass
            
        # Try Nmap Hostname Resolution
        if not hostname:
            try:
                nm.scan(hosts=ip_address, arguments='-sn')
                if ip_address in nm.all_hosts():
                    nmap_host = nm[ip_address].hostname()
                    if nmap_host:
                        hostname = nmap_host
            except Exception:
                pass
                
        # Final Fallback if scanning fails
        if not hostname:
            hostname = f"{clean_vendor}-{index}"
            print(f"  -> Scan failed. Using fallback: {hostname}")
        else:
            # Ensure the scanned hostname is unique just in case
            hostname = f"{hostname}-{index}" 
            print(f"  -> Scan successful! Found: {hostname}")

    # Sanitize hostname for /etc/hosts (only alphanumeric and hyphens allowed)
    safe_hostname = re.sub(r'[^a-zA-Z0-9\-]', '-', hostname).strip('-')
    df_clean.at[index, 'FinalHostname'] = safe_hostname

print('\n--- Final Data Output ---')
print(df_clean[['Address', 'HardwareVendor', 'FinalHostname']].to_markdown())

# Format specifically for /etc/hosts (IP Address and Hostname only)
df_final = df_clean[['Address', 'FinalHostname']]

print(f"\nWriting final output to {OUTPUT_FILE}...")
df_final.to_csv(OUTPUT_FILE, sep='\t', index=False, header=False)

print(f"DONE! Copy the contents of {OUTPUT_FILE} to your /etc/hosts file.")