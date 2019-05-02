#!/usr/bin/python3


#
# Name: Bao Pham
# CS 472
# FTP server
#


import socket
import threading
import time
import os
import sys


def log(func, cmd):
    log_msg = time.strftime("%Y-%m-%d %H-%M-%S [-] " + func)
    print("\033[31m%s\033[0m: \033[32m%s\033[0m" % (log_msg, cmd))


HOST = socket.gethostbyname(socket.gethostname())


class FTPServer(threading.Thread):
    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.user_name = ''
        self.password = ''
        self.isAuthenticated = False
        self.pasv_mode = False
        self.data_sock_addr = None
        self.data_sock_port = None
        self.data_sock = None
        self.data_address = None
        self.server_sock = None
        self.cwd = '.'

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

    # send text to client socket
    def send_command(self, cmd):
        self.client_socket.send(cmd.encode('utf-8'))

    # send data to client socket
    def send_data(self, data):
        self.data_sock.send(data.encode('utf-8'))

    def start_data_sock(self):
        log('start_data_sock', 'Opening a data channel')
        try:
            self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.pasv_mode:
                self.data_sock, self.data_address = self.server_sock.accept()

            else:
                self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.data_sock.connect((self.data_sock_addr, self.data_sock_port))
        except socket.error as err:
            log('start_data_sock', err)

    def stop_data_sock(self):
        log('stop_data_sock', 'Closing a data channel')
        try:
            self.data_sock.close()
            if self.pasv_mode:
                self.server_sock.close()
        except socket.error as err:
            log('stop_data_sock', err)

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

        pathname = path.endswith(os.path.sep) and path or os.path.join(self.cwd, path)
        log('CWD', "Pathname: " + pathname)

        if not os.path.exists(pathname) or not os.path.isdir(pathname):
            self.send_command('550 Directory not exists.\r\n')
            return

        self.cwd = pathname
        self.send_command('250 Changed working directory.\r\n')

    # QUIT command
    def QUIT(self, arg):
        log("QUIT", arg)
        self.send_command('221 Disconnecting... Goodbye!\r\n')

    # PASV command
    def PASV(self, arg):
        log("PASV", arg)
        self.pasv_mode = True
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((socket.gethostname(), 0))
        self.server_sock.listen(5)
        addr, port = self.server_sock.getsockname()
        log("PASV", "Address: " + addr + ", Port: " + str(port))
        self.send_command('200 Entering Passive Mode (%s,%u,%u).\r\n' % (','.join(addr.split('.')), port >> 8 & 0xFF, port & 0xFF))

    # EPSV command
    def EPSV(self, arg):
        log("EPSV", arg)
        self.pasv_mode = True
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((socket.gethostname(), 0))
        self.server_sock.listen(5)
        addr, port = self.server_sock.getsockname()
        log("PASV", "Address: " + addr + ", Port: " + str(port))
        self.send_command(
            '200 Entering Passive Mode (%s,%u,%u).\r\n' % HOST, port >> 8 & 0xFF, port & 0xFF)

    # PORT command
    def PORT(self, cmd):
        log("PORT", cmd)

        if self.pasv_mode:
            self.server_sock.close()
            self.pasv_mode = False

        port_list = cmd.split(',')
        self.data_sock_addr = '.'.join(port_list[:4])
        self.data_sock_port = (int(port_list[4]) << 8) + int(port_list[5])
        log('PORT', 'Address: ' + self.data_sock_addr + ", Port: " + str(self.data_sock_port))

        self.send_command('200 Parsed address and port.\r\n')

    # EPRT command
    def EPRT(self, path):
        log("EPRT", path)

    # RETR command
    def RETR(self, filename):
        log("RETR", filename)
        if not self.isAuthenticated:
            self.send_command('530 User not logged in.\r\n')
            return

        pathname = os.path.join(self.cwd, filename)
        log('RETR', "Pathname: " + pathname)

        if not os.path.exists(pathname):
            return

        try:
            file = open(pathname, 'r')
        except OSError as err:
            log('RETR', err)
            self.send_command(str(err) + '\r\n')
            return

        self.send_command('150 Opening data connection...\r\n')
        self.start_data_sock()
        while True:
            data = file.read(1024)
            if not data:
                break
            self.send_data(data)
        file.close()
        self.stop_data_sock()
        self.send_command('226 Transfer complete.\r\n')

    # STOR command
    def STOR(self, file):
        log("STOR", file)
        if not self.isAuthenticated:
            self.send_command('530 User not logged in.\r\n')
            return

        pathname = os.path.join(self.cwd, file)
        log('STOR', "Pathname: " + pathname)
        try:
            file = open(pathname, 'w')
        except OSError as err:
            log('STOR', err)
            self.send_command(str(err) + '\r\n')
            return

        self.send_command('150 Opening data connection...\r\n')
        self.start_data_sock()
        while True:
            data = self.data_sock.recv(1024)
            if not data:
                break
            file.write(data)
        file.close()
        self.stop_data_sock()
        self.send_command('226 Transfer completed.\r\n')

    # PWD command
    def PWD(self, path):
        log("PWD", path)
        self.send_command(os.path.abspath(self.cwd) + '\r\n')

    # SYST command
    def SYST(self, path):
        log("SYST", path)
        self.send_command(sys.platform + '\r\n')

    # LIST command
    def LIST(self, path):
        log("LIST", path)

        if not self.isAuthenticated:
            self.send_command('530 User not logged in.\r\n')
            return

        if not path:
            pathname = os.path.abspath(self.cwd)
        else:
            pathname = os.path.abspath(os.path.join(self.cwd, path))

        log("LIST", "Pathname: " + pathname)

        if not os.path.exists(pathname):
            self.send_command('550 Path name not found.\r\n')
        else:
            self.send_command('150 Here is listing.===================\r\n')

            # open socket to send data
            self.start_data_sock()
            if not os.path.isdir(pathname):
                file_message = pathname
                self.data_sock.sock(file_message + '\r\n')

            else:
                for file in os.listdir(pathname):
                    file_message = file
                    self.send_data(file_message + '\r\n')

            # close socket after sending data
            self.stop_data_sock()
            log("LIST", "sent list")
            self.send_command('==============226 List done.\r\n')

    # HELP command
    def HELP(self, arg):
        log("HELP", arg)

        help_str = """
                USER [username]                 Send new user information
                PASS [password]                 Password for authentication
                CWD  [dir_path]                 Change working directory.
                QUIT []                         Terminate ftp session and exit
                PASV []                         The directive requires server-DTP in a data port.
                EPSV []                         Enter extended passive mode
                PORT [h1, h2, h3, h4, p1, p2]   Data connection data port
                EPRT []                         Extended data port
                RETR []                         Server sends a copy of a file with the specified path name
                STOR []                         Data is stored as a file server site.
                PWD  []                         Get current working directory.
                SYS  []                         Get server's operating system
                LIST [dir_path or filename]     List file and directory names
                HELP                            Displays help information.\r\n
                """
        self.send_command(help_str)


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
