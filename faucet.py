from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname, getaddrinfo
from config import *
import os
from cryp import encrypt, decrypt

import select
import time

class Broadcast:
    def __init__(self, username: str) -> None:
        self.IP = gethostbyname(gethostname())

        self.udp_server = socket(AF_INET, SOCK_DGRAM)
        self.udp_server.bind((self.IP, 0))
        self.udp_server.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        self.broadcast_data = f"{MAGIC}{username}{SEPARATOR}{self.IP}"
        # interfaces = getaddrinfo(host=None, port=None, family=AF_INET)
        # self.allips = [ip[-1][0] for ip in interfaces]
        # print(self.allips)

    def broadcast(self):
        data = self.broadcast_data.encode()
        # for i in range(256):
        #     for j in range(256):
        #         self.udp_server.sendto(data, (f'10.64.{i}.{j}', BROADCAST_PORT))
        #     print(i)
        # for ip in self.allips:
        self.udp_server.sendto(data, ('<broadcast>', BROADCAST_PORT))
        # print("SENT BROADCAST")
    
    def close(self):
        return self.udp_server.close()

class Detector:
    def __init__(self) -> None:
        self.udp_server = socket(AF_INET, SOCK_DGRAM)
        self.udp_server.bind(('', BROADCAST_PORT))
        
    def detect(self):
        self.to = select.select([self.udp_server], [], [], 5)
        return self.to[0][0].recvfrom(1024)

class Server:
    def __init__(self, username: str, password: str) -> None:
        self.password = password
        self.bc = Broadcast(username)

        self.broadcast_data = MAGIC + self.bc.IP

        self.server = socket()
        self.server.bind((SERVER_HOST, SERVER_PORT))
        self.server.listen(5)
        self.server.settimeout(1)
        
        interfaces = getaddrinfo(host=gethostname(), port=None, family=AF_INET)
        self.allips = [ip[-1][0] for ip in interfaces]
        print(self.allips)

        print(f"[*] Listening as {self.bc.IP}:{SERVER_PORT}")

    # def _broadcast(self):
    #     data = self.broadcast_data.encode()
    #     # for i in range(256):
    #     #     for j in range(256):
    #     #         self.udp_server.sendto(data, (f'10.64.{i}.{j}', BROADCAST_PORT))
    #     #     print(i)
    #     self.udp_server.sendto(data, ('10.64.18.255', BROADCAST_PORT))
    #     print("SENT BROADCAST")

    def listen(self):
        while 1:
            self.bc.broadcast()
            try:
                client_socket, address = self.server.accept()
                print(f"[+] {address} is connected.")
                # self.recieve_file(client_socket)
            except TimeoutError:
                pass
    def close(self):
        self.server.close()
        self.bc.close()

    def recieve_handshake(self, client_socket):
        received = client_socket.recv(HANDSHAKE).decode()
        print(received)
        filename, filesize, extra = received.split(SEPARATOR)
        filename = "rec." + os.path.basename(filename)
        filesize = int(filesize)
        return filename, filesize

    def recieve_file(self, f, password: str, client_socket):
        # with open(filename, "wb") as f:
        #     print()
        #     start = time.time()
        #     done = 0
            # while True:
        tstart = time.time()
        how_much = client_socket.recv(4)
        how_much = int.from_bytes(how_much) # type: ignore
        bytes_read = self._pakka_recv(client_socket, how_much)
        if not bytes_read:
            return False
        try:
            dedata = (decrypt(bytes_read, password))
            f.write(dedata)
            # done += BUFFER_SIZE
            tlapsed = time.time() - tstart
            return BUFFER_SIZE
            # print(f"\r{done}/{filesize} ETA: {elapsed * filesize / done}s | Speed: {BUFFER_SIZE / (tlapsed * 1024 * 1024)} MB/s          ", end="")
        except Exception as e:
            print("REC:", bytes_read, how_much, e, "h")
            quit()
        client_socket.close()

    @staticmethod
    def _pakka_recv(sock, MSGLEN):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)


class Client:
    def __init__(self, password: str | None = None) -> None:
        self.password = password
        self.detector = Detector()
        self.host = None
        self.server = socket()

        self.hosts = {}

    def find_host(self):
        try:
            data, addr = self.detector.detect() #wait for a packet
            print(data)
        except IndexError:
            return {}
        if data.startswith(MAGIC.encode()):
            username, host = data[len(MAGIC):].decode().split(SEPARATOR)
            self.hosts[username] = host
            return self.hosts
        return {}
    
    def connect(self, ip):
        self.server.connect((ip, SERVER_PORT))

    def send_handshake(self, filename: str, password: str | None = None):
        if password is not None:
            self.password = password
        elif self.password is None:
            raise ValueError("Password Needed")
        filesize = os.path.getsize(filename)
        to_send = f"{filename}{SEPARATOR}{filesize}{SEPARATOR}"
        final_send = to_send + "0" * (HANDSHAKE - len(to_send))
        self.server.send(final_send.encode())

        # with open(filename, "rb") as f:
    def send_packet(self, f, password: str):
        bytes_read = f.read(BUFFER_SIZE)
        print(len(bytes_read))
        if len(bytes_read) == 0: print(bytes_read)
        if not bytes_read:
            print("ew")
            return False
        sending = encrypt(bytes_read, password)
        sending_with_length = len(sending).to_bytes(4) + sending
        # print("Sent:", sending, len(sending))
        try:self.server.sendall(sending_with_length); return True
        except:print(sending)


    def close(self):
        self.server.close()
        self.detector.udp_server.close()


def main():
    pass
    # s = Server("?")
    # s.listen()

if __name__ == "__main__":
    main()