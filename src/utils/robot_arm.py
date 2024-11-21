#! /usr/bin/env python3

import socket
import time

from utils.ip import get_ip


class RobotArm:

    # host = ""
    # port_ur = ""
    # port_gripper = ""
    # ip = ""

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

    def start_pos(self):
        joint_angles = [0, -1.57, 0, 0, 0, 0]  # upright position
        self.send_joint_command(joint_angles, "j")

    def open_gripper(self):
        self.send_gripper_command(150)

    def close_gripper(self):
        self.send_gripper_command(200)

    def send_joint_command(self, joint_angles, mode="l"):
        values = ", ".join(
            ["{:.2f}".format(i) if type(i) == float else str(i) for i in joint_angles]
        )
        self.socket_ur.send(
            str.encode("move" + mode + "([" + values + "], a=1.4, v=1.05, t=0, r=0)\n")
            # str.encode("movel([" + values + "])\n")
        )

    def send_gripper_command(self, value):
        if value >= 0 and value <= 255:
            command = "SET POS " + str(value) + "\n"
            self.socket_gripper.send(str.encode(command))
            # make the gripper move
            self.socket_gripper.send(b"SET GTO 1\n")

    def set_gripper_speed(self):
        pass

    def close_connection(self):
        self.socket_ur.close()
        self.socket_gripper.close()
        self.server_socket.close()

    def get_inverse_kinematics(self, pose):
        # Create the TCP/IP socket and set SO_REUSEADDR to reuse the port
        # # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # # server_socket.setsockopt(
        # # socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        # # )  # Allow port reuse

        # # socket_ur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # # socket_ur.connect((ROBOT_IP, ROBOT_PORT))

        # Bind the socket to the IP address and port of the Python client
        # server_socket.bind((LAPTOP_IP, 30003))
        # server_socket.listen(1)

        # URScript command to be sent to the robot
        values = ", ".join(
            ["{:.2f}".format(i) if type(i) == float else str(i) for i in pose]
        )

        command = (
            """
        desired_pose = p["""
            + values
            + ''']
        joints = get_inverse_kin(desired_pose)
        socket_open("'''
            + self.ip
            + """", 30003)
        socket_send_string(to_str(joints))
        socket_close()
        """
        )

        # Send the URScript command to the robot
        full_command = f"def my_prog():\n{command}\nend\n"
        try:
            self.socket_ur.sendall(full_command.encode("utf-8"))
            print(f"Sent URScript command: {full_command}")
        except socket.error as e:
            print(f"Socket error: {e}")

        # Accept the incoming connection from the robot
        print("Waiting for connection from the robot...")
        conn, addr = self.server_socket.accept()
        print(f"Connection from {addr}")

        try:
            # Receive the data (Inverse Kinematics)
            data = conn.recv(1024).decode()
            print(f"Received Inverse Kinematics: {data}")

            # Convert the received string to a list of joint angles
            joint_angles = [float(angle) for angle in data.strip("[]").split(",")]

            # Return the joint angles
            return joint_angles
        finally:
            conn.close()


# import math


# def deg_to_rad(degrees):
#     return math.radians(degrees)


# if __name__ == "__main__":
#     robot = RealRobotArm()

#     robot.close_connection()
