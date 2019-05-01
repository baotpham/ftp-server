#!/usr/bin/python3


#
# Name: Bao Pham
# CS 472
# FTP server
#


import socket
import time


def log(func, cmd):
    log_msg = time.strftime("%Y-%m-%d %H-%M-%S [-] " + func)
    print("\033[31m%s\033[0m: \033[32m%s\033[0m" % (log_msg, cmd))


class FTPServer:
    def __init__(self, client_socket, client_address):
        self.client_socket = client_socket
        self.client_address = client_address

    def do_protocol(self):
        log('Client Connected', "Connected with: %s:%s" % self.client_address)

        while True:
            try:
                data = self.client_socket.readcv(1024)
                print(data)

                try:
                    cmd = data.decode('utf-8')
                except AttributeError:
                    cmd = data
                log('Received data', cmd)
                if not cmd:
                    break
            except socket.error as err:
                log('Receive', err)

        #     try:
        #         cmd, arg = cmd[:4].strip().upper(), cmd[4:].strip() or None
        #         func = getattr(self, cmd)
        #         func(arg)
        #     except AttributeError as err:
        #         self.send_command('500 Syntax error, command unrecognized. This may include errors such as '
        #                           'command line too long.\r\n')
        #         log('Receive', err)

    def send_command(self, cmd):
        self.client_socket.send(cmd.encode())


def main():
a
    port = input("Port (default port 10021 if blank): ")
    if not port:
        port = 10021

    # data_port = input("Data Port (default port 20): ")
    # if not data_port:
    #     data_port = 10020

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((socket.gethostname(), port))
    server_socket.listen(5)
    log("Server started", "Waiting for connection on: " + socket.gethostbyname(socket.gethostname()) + " " + str(port))

    while True:
        # accept connections from outside
        (client_socket, address) = server_socket.accept()
        ftp_server = FTPServer(client_socket, address)
        ftp_server.do_protocol()
        client_socket.close()


if __name__ == "__main__":
    main()
