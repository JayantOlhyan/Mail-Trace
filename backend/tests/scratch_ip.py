import ipaddress
import socket
import urllib.parse

def test_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        print(f"{ip_str} normal: {ip}")
        return
    except ValueError:
        pass
    
    try:
        if ip_str.startswith("0x"):
            ip = ipaddress.ip_address(int(ip_str, 16))
        elif ip_str.startswith("0"):
            ip = ipaddress.ip_address(int(ip_str, 8))
        else:
            ip = ipaddress.ip_address(int(ip_str))
        print(f"{ip_str} int: {ip}")
    except ValueError:
        print(f"{ip_str} failed int parsing")

test_ip("127.0.0.1")
test_ip("2130706433")
test_ip("0x7f000001")
test_ip("017700000001") # octal
test_ip("0x7f.0.0.1")

# Let's see what socket.gethostbyname does
try:
    print("socket 0177.0.0.1:", socket.gethostbyname("0177.0.0.1"))
except Exception as e:
    print(e)
try:
    print("socket 0x7f.0.0.1:", socket.gethostbyname("0x7f.0.0.1"))
except Exception as e:
    print(e)
try:
    print("socket 2130706433:", socket.gethostbyname("2130706433"))
except Exception as e:
    print(e)
