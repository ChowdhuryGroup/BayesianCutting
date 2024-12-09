import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Load points from file
file_path = "2024-12-06CutToAnalyze/backside/test.txt"  # Replace with actual path
points = np.loadtxt(file_path)

# Separate x and y coordinates
x_coords = points[:, 0]
y_coords = points[:, 1]

# Calculate cumulative distances along the loop
distances = np.sqrt(np.diff(x_coords) ** 2 + np.diff(y_coords) ** 2)
cumulative_distances = np.insert(np.cumsum(distances), 0, 0)  # Include starting point

# Create uniform samples along the cumulative distances
num_points = 1000  # Desired number of uniformly spaced points
uniform_distances = np.linspace(0, cumulative_distances[-1], num_points)

# Interpolate x and y coordinates at uniform distances
x_interp = interp1d(cumulative_distances, x_coords, kind="cubic")(uniform_distances)
y_interp = interp1d(cumulative_distances, y_coords, kind="cubic")(uniform_distances)

# Recalculate the center
center_x = np.mean(x_interp)
center_y = np.mean(y_interp)

# Calculate distances from the center
new_distances = np.sqrt((x_interp - center_x) ** 2 + (y_interp - center_y) ** 2)

# Find the closest and furthest distances
min_distance = np.min(new_distances)
max_distance = np.max(new_distances)

# Find the corresponding points
closest_point = np.array(
    [x_interp[np.argmin(new_distances)], y_interp[np.argmin(new_distances)]]
)
furthest_point = np.array(
    [x_interp[np.argmax(new_distances)], y_interp[np.argmax(new_distances)]]
)

# Plot the resampled points and calculated features
plt.figure(figsize=(10, 10))
plt.scatter(x_interp, y_interp, color="blue", label="Uniformly Resampled Points")
plt.scatter(center_x, center_y, color="red", label="Center")
plt.scatter(closest_point[0], closest_point[1], color="green", label="Closest Point")
plt.scatter(
    furthest_point[0], furthest_point[1], color="purple", label="Furthest Point"
)

# Draw circles for the closest and furthest distances
circle_closest = plt.Circle(
    (center_x, center_y),
    min_distance,
    color="green",
    fill=False,
    linestyle="--",
    label="Closest Radius",
)
circle_furthest = plt.Circle(
    (center_x, center_y),
    max_distance,
    color="purple",
    fill=False,
    linestyle="--",
    label="Furthest Radius",
)
plt.gca().add_artist(circle_closest)
plt.gca().add_artist(circle_furthest)

plt.legend(loc="upper left")
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Uniformly Resampled Points and Radii")
plt.axis("equal")
plt.show()

# Print results
print(f"Center: ({center_x:.2f}, {center_y:.2f})")
print(
    f"Closest Point: ({closest_point[0]:.2f}, {closest_point[1]:.2f}) with Distance: {min_distance:.2f}"
)
print(
    f"Furthest Point: ({furthest_point[0]:.2f}, {furthest_point[1]:.2f}) with Distance: {max_distance:.2f}"
)


# THIS WORKS GOOD FOR UNIFORM SPACED POINTS
# import numpy as np
# import matplotlib.pyplot as plt

# # Load points from file
# file_path = "2024-12-06CutToAnalyze/backside/test.txt"  # Replace with actual path
# points = np.loadtxt(file_path)

# # Separate x and y coordinates
# x_coords = points[:, 0]
# y_coords = points[:, 1]

# # Calculate the center of the points
# center_x = np.mean(x_coords)
# center_y = np.mean(y_coords)
# center = np.array([center_x, center_y])

# # Calculate distances from the center
# distances = np.sqrt((x_coords - center_x) ** 2 + (y_coords - center_y) ** 2)

# # Find the closest and furthest distances
# min_distance = np.min(distances)
# max_distance = np.max(distances)

# # Find the corresponding points
# closest_point = points[np.argmin(distances)]
# furthest_point = points[np.argmax(distances)]

# # Plot the points, center, and radii
# plt.figure(figsize=(10, 10))
# plt.scatter(x_coords, y_coords, color="blue", label="Points")
# plt.scatter(center_x, center_y, color="red", label="Center")
# plt.scatter(closest_point[0], closest_point[1], color="green", label="Closest Point")
# plt.scatter(
#     furthest_point[0], furthest_point[1], color="purple", label="Furthest Point"
# )

# # Draw circles for the closest and furthest distances
# circle_closest = plt.Circle(
#     (center_x, center_y),
#     min_distance,
#     color="green",
#     fill=False,
#     linestyle="--",
#     label="Closest Radius",
# )
# circle_furthest = plt.Circle(
#     (center_x, center_y),
#     max_distance,
#     color="purple",
#     fill=False,
#     linestyle="--",
#     label="Furthest Radius",
# )
# plt.gca().add_artist(circle_closest)
# plt.gca().add_artist(circle_furthest)

# plt.legend(loc="upper left")
# plt.xlabel("X")
# plt.ylabel("Y")
# plt.title("Points with Closest and Furthest Radii from Center")
# plt.axis("equal")
# plt.show()

# # Print results
# print(f"Center: ({center_x:.2f}, {center_y:.2f})")
# print(
#     f"Closest Point: ({closest_point[0]:.2f}, {closest_point[1]:.2f}) with Distance: {min_distance:.2f}"
# )
# print(
#     f"Furthest Point: ({furthest_point[0]:.2f}, {furthest_point[1]:.2f}) with Distance: {max_distance:.2f}"
# )
