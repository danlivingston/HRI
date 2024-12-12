#! /usr/bin/env python3

import socket

from loguru import logger

from utils.ip import get_ip


class RobotArm:
    def __init__(self):

        # TODO: import from env
        self.host = "192.168.1.11"
        self.port_ur = 30002
        self.port_gripper = 63352
        self.ip = get_ip()

        # Create the TCP/IP socket and set SO_REUSEADDR to reuse the port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )  # Allow port reuse

        # Bind the socket to the IP address and port of the Python client
        self.server_socket.bind((self.ip, 30003))
        self.server_socket.listen(1)

        # Create socket connection to robot arm and gripper
        self.socket_ur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_ur.connect((self.host, self.port_ur))
        self.socket_gripper = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_gripper.connect((self.host, self.port_gripper))
        # activate the gripper
        self.socket_gripper.sendall(b"SET ACT 1\n")

    # def assume_start_pos(self):
    #     joint_angles = [0, -1.57, 0, 0, 0, 0]  # upright position
    #     self.send_move_command(joint_angles, "j")

    def open_gripper(self):
        self.send_gripper_command(153)

    def half_open_gripper(self):
        self.send_gripper_command(180)

    def close_gripper(self):
        self.send_gripper_command(185)

    def send_move_command(self, values, mode="j", pose=False, t=2, a=0.25):
        values = ", ".join(
            ["{:.4f}".format(i) if type(i) is float else str(i) for i in values]
        )
        prefix = "p" if pose else ""
        cmd = str.encode(f"move{mode}({prefix}[{values}],a={a},t={t})\n")
        self.socket_ur.send(cmd)
        logger.debug(f"sent command: {cmd}")

    def send_gripper_command(self, value):
        if value >= 0 and value <= 255:
            command = "SET POS " + str(value) + "\n"
            self.socket_gripper.send(str.encode(command))
            # make the gripper move
            self.socket_gripper.send(b"SET GTO 1\n")

    def rotate_gripper_90deg(self):
        cmd = str.encode("speedj([0,0,0,0,0,3.14],3,1)\n")
        self.socket_ur.send(cmd)
        logger.debug(f"sent command: {cmd}")

    def set_gripper_speed(self):
        pass

    def close_connection(self):
        self.socket_ur.close()
        self.socket_gripper.close()
        self.server_socket.close()
