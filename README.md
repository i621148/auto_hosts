# auto_hosts

Automatically generate a /etc/hosts file for your Pi-hole based on all current MAC address connections.

In the good ole days before every calculator could generate a dynamic MAC address, it was easy to keep track of what device was on your network.
Now we have stuff to do.  We can't be log stalking every ip address on our home networks.  There can be easily a hundred IoT devices on the average home network.
I wrote this program because dynamic MAC addresses have taken the fun out of using Pi-hole and diligently observing what is doing what on your network.

Visit site below and sign up for free API key  
https://macaddress.io/api

Replace                  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx with your key from macaddress.io/api  
os.environ['API_KEY'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

Copy contents of hosts3.txt to your /etc/hosts file.  
You can also copy contents to /etc/pihole/local.list if you want the new alias to work on a network wide level.  

Pi-hole>Settings>Restart DNS resolver

Enjoy!

Tested with:  
Linux raspberrypi 5.10.103-v7+ #1529 SMP Tue Mar 8 12:21:37 GMT 2022 armv7l GNU/Linux  
Python 3.7.3  

I am not affiliated with Pi-hole (https://pi-hole.net/) in any way other than being an enthusiastic user and enjoyer of their hard work.  
I am not the creator or source of Pi-hole and my project is not approved, sponsored, or affiliated with Pi-hole or the community.  
There is no commercial purpose behind the use of this project and I am not offering Pi-hole commercially under the same domain name.  
