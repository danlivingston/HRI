#! /usr/bin/env python3

"""
BSD 3-Clause License

Copyright (c) 2023, Shawn Armstrong

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import socket
import sys
import rospy

from package import Package
from sensor_msgs.msg import JointState
from urdf_parser_py.urdf import URDF

PORT = 30001


class URPrimaryClient:

    def __init__(self):
        self.joint_state_publisher = rospy.Publisher(
            "my_joint_states", JointState, queue_size=10
        )
        rospy.init_node("my_joint_state_publisher")
        self.rate = rospy.Rate(10)
        rospy.sleep(3.0)

    def run(self):

        robot = URDF.from_parameter_server()
        root = robot.get_root()
        tip = "tool0"
        joint_names = robot.get_chain(root, tip, joints=True, links=False, fixed=False)

        host = rospy.get_param("robot_ip")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:

            clientSocket.settimeout(4)
            try:
                clientSocket.connect((host, PORT))
            except socket.timeout as e:
                rospy.logerr(f"Timeout error: {e}")
                sys.exit(1)
            except socket.error as e:
                rospy.logerr(f"Could not connect to {host}:{PORT} Error: {e}")
                sys.exit(1)

            rospy.loginfo(f"Established connection to {host}:{PORT}")

            joint_angles = [0, 0, 0, 0, 0, 0]  # in radians

            # create the joint state messages
            js = JointState()
            js.name = joint_names
            js.position = joint_angles

            # publish the joint state values
            while not rospy.is_shutdown():

                # Receives message from UR controller.
                new_message = clientSocket.recv(4096)

                # Creates package based on message received.
                new_package = Package(new_message)
                subpackage = new_package.get_subpackage("Joint Data")
                if subpackage is not None:
                    joint_angles = [
                        subpackage.subpackage_variables.Joint1_q_actual,
                        subpackage.subpackage_variables.Joint2_q_actual,
                        subpackage.subpackage_variables.Joint3_q_actual,
                        subpackage.subpackage_variables.Joint4_q_actual,
                        subpackage.subpackage_variables.Joint5_q_actual,
                        subpackage.subpackage_variables.Joint6_q_actual,
                    ]

                js.position = joint_angles
                # Publish Joint Angles
                self.joint_state_publisher.publish(js)
                self.rate.sleep()

            clientSocket.close()
            clientSocket = -1
            rospy.loginfo(f"Closed connection to {HOST}:{PORT} ")


if __name__ == "__main__":
    client = URPrimaryClient()
    client.run()
