#! /usr/bin/env python3

import socket
import time

from utils.package import Package


class RealRobotArm:

    def __init__(self):

        host = "192.168.1.11"
        port_ur = 30002
        port_gripper = 63352

        # Create socket connection to robot arm and gripper
        self.socket_ur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_ur.connect((host, port_ur))
        self.socket_gripper = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_gripper.connect((host, port_gripper))
        # activate the gripper
        self.socket_gripper.sendall(b"SET ACT 1\n")

    def send_joint_command(self, joint_angles):
        values = ", ".join(
            ["{:.2f}".format(i) if type(i) == float else str(i) for i in joint_angles]
        )
        self.socket_ur.send(
            # str.encode("movej([" + values + "], a=1.4, v=1.05, t=0, r=0)\n")
            str.encode("movej([" + values + "], a=1.4, v=1.05, t=0, r=0)\n")
            # str.encode("movel([" + values + "])\n")
            # str.encode(
            #     "get_inverse_kin(p[.1,.2,.2,0,3.14,0], [0.,3.14,1.57,.785,0,0])\n"
            # )
            # str.encode(
            #     "get_inverse_kin_has_solution(p[.1,.2,.2,0,3.14,0], [0.,3.14,1.57,.785,0,0])\n"
            # )
        )
        # response = self.socket_ur.recv(4096)  # Adjust buffer size as needed
        # new_package = Package(response)
        # # subpackage = new_package.get_subpackage("Joint Data")
        # subpackage = new_package.get_subpackage("Joint Data")
        # if subpackage is not None:
        #     joint_angles = [
        #         subpackage.subpackage_variables.Joint1_q_actual,
        #         subpackage.subpackage_variables.Joint2_q_actual,
        #         subpackage.subpackage_variables.Joint3_q_actual,
        #         subpackage.subpackage_variables.Joint4_q_actual,
        #         subpackage.subpackage_variables.Joint5_q_actual,
        #         subpackage.subpackage_variables.Joint6_q_actual,
        #     ]

        # print("Response from get_inverse_kin:", repr(new_package))
        # print("Sub:", subpackage)
        # print("JA:", joint_angles)

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


import math


def deg_to_rad(degrees):
    return math.radians(degrees)


if __name__ == "__main__":
    robot = RealRobotArm()

    time.sleep(2)
    # send joint angles
    joint_angles = [0, -1.57, 0, 0, 0, 0]  # upright position
    robot.send_joint_command(joint_angles)
    # robot.send_gripper_command(150)
    # time.sleep(5)
    # joint_angles = [
    #     deg_to_rad(74.5),
    #     deg_to_rad(-28),
    #     deg_to_rad(31),
    #     deg_to_rad(-97),
    #     deg_to_rad(-87.5),
    #     deg_to_rad(167),
    # ]
    # robot.send_joint_command(joint_angles)
    # time.sleep(5)
    # robot.send_gripper_command(200)
    # time.sleep(1)
    # joint_angles = [
    #     deg_to_rad(90),
    #     deg_to_rad(-40),
    #     deg_to_rad(31),
    #     deg_to_rad(-97),
    #     deg_to_rad(-87.5),
    #     deg_to_rad(167),
    # ]
    # robot.send_joint_command(joint_angles)
    # time.sleep(2)
    # joint_angles = [
    #     deg_to_rad(90),
    #     deg_to_rad(-28),
    #     deg_to_rad(31),
    #     deg_to_rad(-97),
    #     deg_to_rad(-87.5),
    #     deg_to_rad(167),
    # ]
    # robot.send_joint_command(joint_angles)
    # time.sleep(1)
    # robot.send_gripper_command(150)
    # time.sleep(1)
    # joint_angles = [
    #     deg_to_rad(90),
    #     deg_to_rad(-40),
    #     deg_to_rad(31),
    #     deg_to_rad(-97),
    #     deg_to_rad(-87.5),
    #     deg_to_rad(167),
    # ]
    # robot.send_joint_command(joint_angles)
    # time.sleep(8)

    # robot.send_joint_command(joint_angles)
    # robot.send_gripper_command(0)
    # time.sleep(10)
    # robot.send_gripper_command(180)
    # # joint_angles = [0, -1.57, 0, -2, 0, 0]
    # # robot.send_joint_command(joint_angles)

    # # send gripper command
    # # set requested postion to 100 (value between 0-255)
    # # print("G2")
    # time.sleep(10)
    # # print("G3")
    # robot.send_gripper_command(150)
    # time.sleep(10)
    # robot.send_gripper_command(0)

    robot.close_connection()
