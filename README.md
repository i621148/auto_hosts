# auto_hosts

Automatically generate a `/etc/hosts` file for your Pi-hole based on all current MAC address connections.

In the good ole days before every calculator could generate a dynamic MAC address, it was easy to keep track of what device was on your network. Now we have stuff to do. We can't be log stalking every IP address on our home networks. There can easily be a hundred IoT devices on the average home network. 

I wrote this program because dynamic MAC addresses have taken the fun out of using Pi-hole and diligently observing what is doing what on your network.

**Update:** This script now runs 100% locally! It downloads the official IEEE MAC address registry directly to your Raspberry Pi, meaning it runs instantly and requires no API keys or rate limits.

### Installation

1. Clone the repository and navigate into the directory:
```bash
git clone [https://github.com/i621148/auto_hosts.git](https://github.com/i621148/auto_hosts.git)
cd auto_hosts
```

2. Create and activate a Python virtual environment (recommended to prevent system package conflicts):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Usage

1. Run the script (make sure your virtual environment is active):
```bash
python3 auto_hosts.py
```

2. Copy the contents of the newly generated `hosts_pihole.txt` to your `/etc/hosts` file.

3. Restart your Pi-hole service to apply the names. **Note: For Pi-hole v6+, the standard restart commands have changed.**
   * **CLI (Recommended):** `sudo systemctl restart pihole-FTL`
   * **GUI:** Go to `Settings > System`, toggle on **Expert Mode**, and select Restart FTL/DNS.

Enjoy!

---
**Tested with:** * Linux raspberrypi 6.12.62+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.12.62-1+rpt1~bookworm (2026-01-19) aarch64 GNU/Linux  
* Python 3.11+ 

**Disclaimer:** I am not affiliated with Pi-hole (https://pi-hole.net/) in any way other than being an enthusiastic user and enjoyer of their hard work. I am not the creator or source of Pi-hole, and my project is not approved, sponsored, or affiliated with Pi-hole or the community. There is no commercial purpose behind the use of this project, and I am not offering Pi-hole commercially under the same domain name.
