import socket
import threading
import ipaddress

class Device:
    def __init__(self):
        self.subscriptions = []

    def add_sub(self, srcCh, dstIP, dstCh):
        if (srcCh, dstIP, dstCh) not in self.subscriptions:
            self.subscriptions.append((srcCh, dstIP, dstCh))
    
    def del_sub(self, srcCh, dstIP, dstCh):
        if (srcCh, dstIP, dstCh) in self.subscriptions:
            self.subscriptions.remove(srcCh, dstIP, dstCh)

    def del_all_subs(self):
        self.subscriptions.clear()
    
    def print_device(self):
        for (sc, di, dc) in self.subscriptions:
            print(f'ch{sc + 1} ---> [{di}]: ch{dc + 1}')

def watcher():
    while True:
        (data, addr) = inp.recvfrom(4)
        if data[0] == 128: #\x80
            if addr[0] not in devices.keys():
                devices[addr[0]] = Device()
            if data[2] > 0:
                devices[addr[0]].add_sub(data[1], data[2], data[3])

def fill_all_channels(srcIP, srcCh, dstIP):
    for i in range(16):
        out.sendto(bytes([15, int(srcCh) - 1, int(dstIP),  int(i)]),(srcIP, MOE_PORT))

def del_all_channels(srcIP, srcCh, dstIP):
    for i in range(16):
        out.sendto(bytes([14, int(srcCh) - 1, int(dstIP), int(i)]),(srcIP, MOE_PORT))



devices = dict()

MOE_PORT = 50000
MY_IP = socket.gethostbyname(socket.gethostname())
MASK = '255.255.255.0'
#BROADCAST_IP = '192.168.2.255'

HOST = ipaddress.IPv4Address(MY_IP)
NET = ipaddress.IPv4Network(MY_IP + '/' + MASK, False)

BROADCAST_IP = str(NET.broadcast_address)

out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

inp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
inp.bind((MY_IP, MOE_PORT))

#out.sendto(b'\x08\x08\x08\x08', ('192.168.2.255', MOE_PORT))




thread = threading.Thread(target=watcher)
thread.start()

out.sendto(b'\x08\x08\x08\x08', (BROADCAST_IP, MOE_PORT))

print("****** MoE Matrix Editor v0.5 ****** \n'print' \tsee devices and their connections on the network \n'add' \t\tadd connection, from one device to another \n'del' \t\tdelete connection\n'reload' \treload the session. (e.g. when Arduino was restarted)")
#out.sendto(b'\xFF\xFF\xFF\xFF', ('192.168.2.116', MOE_PORT))
#out.sendto(b'\x0F\x04\x72\x03', ('192.168.2.116', MOE_PORT))
#out.sendto(b'\x08\x08\x08\x08', ('192.168.2.255', MOE_PORT))

while True:
    query = input()
    if query == 'print':
        for d in devices.keys():
            print(f'___[{d}]___')
            devices[d].print_device()
    if query == 'reload':
        devices.clear()
        out.sendto(b'\x08\x08\x08\x08', (BROADCAST_IP, MOE_PORT))
        print("*** session has been reloaded ***")
    if query == 'add':
        print("IP address: ", end=" ")
        address = input()
        print('sourceChannel destinationIP destinationChannel: ', end=" ")
        sc, dip, dc = input().split()
        if int(dc) == 255:
            fill_all_channels(address, sc, dip)
        else:
            out.sendto(bytes([15, int(sc) - 1, int(dip), int(dc) - 1]),(address, MOE_PORT))
        out.sendto(b'\x08\x08\x08\x08', (address, MOE_PORT))
        print("*** added ***")
    if query == 'del':
        print("IP address: ", end=" ")
        address = input()
        print('sourceChannel destinationIP destinationChannel: ', end=" ")
        sc, dip, dc = input().split()
        del devices[address]
        if int(dc) == 255:
            del_all_channels(address, sc, dip)
        else:
            out.sendto(bytes([14, int(sc) - 1, int(dip), int(dc) - 1]),(address, MOE_PORT))
        out.sendto(b'\x08\x08\x08\x08', (address, MOE_PORT))  
        print("*** deleted ***")     
    