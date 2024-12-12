import json

import matplotlib.pyplot as plt

# Load board positions from JSON file
with open("board_positions.json", "r") as file:
    board_positions = json.load(file)

# Extract positions
hover_x_positions = []
hover_y_positions = []
hover_z_positions = []

pickup_x_positions = []
pickup_y_positions = []
pickup_z_positions = []

place_x_positions = []
place_y_positions = []
place_z_positions = []

board_hover_values = board_positions["hover"]["values"]
hover_x_positions.append(board_hover_values[0])
hover_y_positions.append(board_hover_values[1])
hover_z_positions.append(board_hover_values[2])

board_discard_values = board_positions["discard"]["values"]
place_x_positions.append(board_discard_values[0])
place_y_positions.append(board_discard_values[1])
place_z_positions.append(board_discard_values[2])


for pos in board_positions.values():
    try:
        hover_values = pos["hover"]["values"]
        pickup_values = pos["pickup"]["values"]
        place_values = pos["place"]["values"]

        hover_x_positions.append(hover_values[0])
        hover_y_positions.append(hover_values[1])
        hover_z_positions.append(hover_values[2])

        pickup_x_positions.append(pickup_values[0])
        pickup_y_positions.append(pickup_values[1])
        pickup_z_positions.append(pickup_values[2])

        place_x_positions.append(place_values[0])
        place_y_positions.append(place_values[1])
        place_z_positions.append(place_values[2])
    except:  # noqa: B001, E722
        print(f"err pos {pos}")
        pass

# Plot the 2D positions
plt.figure(figsize=(8, 8))
plt.scatter(hover_x_positions, hover_y_positions, c="blue", marker="o", label="Hover")
plt.scatter(pickup_x_positions, pickup_y_positions, c="red", marker="x", label="Pickup")
plt.scatter(place_x_positions, place_y_positions, c="green", marker="^", label="Place")
plt.title("Board Positions (2D)")
plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.legend()
plt.grid(True)
plt.gca().set_aspect("equal", adjustable="box")
plt.show()

# Plot the 3D positions
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection="3d")
ax.scatter(
    hover_x_positions,
    hover_y_positions,
    hover_z_positions,
    c="blue",
    marker="o",
    label="Hover",
)
ax.scatter(
    pickup_x_positions,
    pickup_y_positions,
    pickup_z_positions,
    c="red",
    marker="x",
    label="Pickup",
)
ax.scatter(
    place_x_positions,
    place_y_positions,
    place_z_positions,
    c="green",
    marker="^",
    label="Place",
)
# Calculate the limits for each axis
x_limits = ax.get_xlim3d()
y_limits = ax.get_ylim3d()
z_limits = ax.get_zlim3d()

# Find the maximum range
max_range = max(
    x_limits[1] - x_limits[0], y_limits[1] - y_limits[0], z_limits[1] - z_limits[0]
)

# Set the limits for each axis to be the same
ax.set_xlim3d([x_limits[0], x_limits[0] + max_range])
ax.set_ylim3d([y_limits[0], y_limits[0] + max_range])
ax.set_zlim3d([z_limits[0], z_limits[0] + max_range])

# Set the aspect ratio to be equal
ax.set_box_aspect([1, 1, 1])  # Aspect ratio is 1:1:1

# Set the title and labels
ax.set_title("Board Positions (3D)")
ax.set_xlabel("X Position")
ax.set_ylabel("Y Position")
ax.set_zlabel("Z Position")
ax.legend()

# Show the plot
plt.show()
