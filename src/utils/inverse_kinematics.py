import socket

ROBOT_IP = "192.168.1.11"
LAPTOP_IP = "192.168.1.208"  # own ip of client PC!!!
ROBOT_PORT = 30002


def get_inverse_kinematics():
    # Create the TCP/IP socket and set SO_REUSEADDR to reuse the port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
    )  # Allow port reuse

    socket_ur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_ur.connect((ROBOT_IP, ROBOT_PORT))

    # Bind the socket to the IP address and port of the Python client
    server_socket.bind((LAPTOP_IP, 30003))
    server_socket.listen(1)

    # URScript command to be sent to the robot
    command = (
        '''
    desired_pose = p[0.2, 0.2, 0.2, 0, 1.7, 0]
    joints = get_inverse_kin(desired_pose)
    socket_open("'''
        + LAPTOP_IP
        + """", 30003)
    socket_send_string(to_str(joints))
    socket_close()
    """
    )

    # Send the URScript command to the robot
    full_command = f"def my_prog():\n{command}\nend\n"
    try:
        socket_ur.sendall(full_command.encode("utf-8"))
        print(f"Sent URScript command: {full_command}")
    except socket.error as e:
        print(f"Socket error: {e}")

    # Accept the incoming connection from the robot
    print("Waiting for connection from the robot...")
    conn, addr = server_socket.accept()
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
        server_socket.close()


# Example usage
if __name__ == "__main__":
    result = get_inverse_kinematics()
    print(f"Calculated joint angles: {result}")
