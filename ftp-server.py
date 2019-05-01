#!/usr/bin/python3


#
# Name: Bao Pham
# CS 472
# FTP server
#


import socket
import threading
import time


def log(func, cmd):
    log_msg = time.strftime("%Y-%m-%d %H-%M-%S [-] " + func)
    print("\033[31m%s\033[0m: \033[32m%s\033[0m" % (log_msg, cmd))


class FTPServer(threading.Thread):
    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.user_name = ''
        self.password = ''
        self.isAuthenticated = False

    def run(self):
        self.do_protocol()

    def do_protocol(self):
        log('Client Connected', "Connected with: %s:%s" % self.client_address)
        self.send_command('220 Welcome to Bao\'s FTP server\r\n')

        cmd = ''

        while True:
            try:
                data = self.client_socket.recv(1024).rstrip()
                try:
                    cmd = data.decode('utf-8')
                except AttributeError:
                    cmd = data

                log('Received data', cmd)
                if not cmd:
                    break
            except socket.error as err:
                log('Receive', err)

            try:
                cmd, arg = cmd[:4].strip().upper(), cmd[4:].strip() or None
                func = getattr(self, cmd)
                func(arg)
            except AttributeError as err:
                self.send_command('500 Syntax error, command unrecognized. This may include errors such as '
                                  'command line too long.\r\n')
                log('Receive', err)

    # send data to client socket
    def send_command(self, cmd):
        self.client_socket.send(cmd.encode('utf-8'))

    # USER command
    def USER(self, user):
        log("USER", user)

        if not user:
            self.send_command('501 Syntax error in parameters or arguments.\r\n')

        elif user != 'cs472':
            self.send_command('530 User not found.\r\n')

        else:
            self.send_command('331 User name okay, need password.\r\n')
            self.user_name = user

    # PASS command
    def PASS(self, password):
        log("PASS", password)
        if not password:
            self.send_command('501 Syntax error in parameters or arguments.\r\n')

        elif not self.user_name:
            self.send_command('503 Bad sequence of commands.\r\n')

        elif password != 'pass':
            self.send_command('530 Authentication Failed.\r\n')

        else:
            self.send_command('230 User logged in, proceed.\r\n')
            self.password = password
            self.isAuthenticated = True

    # CWD command
    def CWD(self, path):
        log("CWD", path)

    # QUIT command
    def QUIT(self, arg):
        log("QUIT", arg)
        self.send_command('221 Disconnecting... Goodbye!\r\n')

    # PASV command
    def PASV(self, path):
        log("PASV", path)


def main():
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
        ftp_server.start()


if __name__ == "__main__":
    main()
