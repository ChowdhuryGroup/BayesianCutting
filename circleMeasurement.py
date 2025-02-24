import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Load points from the file
file_path = "ImagesToTest/2024-12-17/trial 43/4.txt"  # Replace with the correct path
points = np.loadtxt(file_path)

# Ensure the loop is closed by appending the first point to the end
if not np.allclose(points[0], points[-1]):
    points = np.vstack([points, points[0]])

# Separate x and y coordinates
x_coords = points[:, 0]
y_coords = points[:, 1]

# Calculate the area using the Shoelace formula
area = 0.5 * np.abs(
    np.dot(x_coords, np.roll(y_coords, 1)) - np.dot(y_coords, np.roll(x_coords, 1))
)

# Correct centroid calculation using the Shoelace formula
cx = np.abs(
    (1 / (6 * area))
    * np.sum(
        (x_coords + np.roll(x_coords, 1))
        * (x_coords * np.roll(y_coords, 1) - np.roll(x_coords, 1) * y_coords)
    )
)
cy = np.abs(
    (1 / (6 * area))
    * np.sum(
        (y_coords + np.roll(y_coords, 1))
        * (x_coords * np.roll(y_coords, 1) - np.roll(x_coords, 1) * y_coords)
    )
)

centroid = np.array([cx, cy])

# Debug: Print the computed centroid
print(f"Computed Center of Mass: ({cx:.2f}, {cy:.2f})")

# Calculate distances from the centroid to each point
distances = np.sqrt((x_coords - cx) ** 2 + (y_coords - cy) ** 2)

# Find the closest and furthest points
min_distance = np.min(distances)
max_distance = np.max(distances)
closest_point = points[np.argmin(distances)]
furthest_point = points[np.argmax(distances)]
rms = np.sqrt(np.mean((distances - np.mean(distances)) ** 2))
perimeter = np.sum(np.sqrt(np.diff(x_coords) ** 2 + np.diff(y_coords) ** 2))

# Plot the results
plt.figure(figsize=(10, 10))
plt.plot(x_coords, y_coords, color="blue", label="Original Shape")
plt.scatter(cx, cy, color="red", label="Center of Mass", zorder=5)
plt.scatter(
    closest_point[0], closest_point[1], color="green", label="Closest Point", zorder=5
)
plt.scatter(
    furthest_point[0],
    furthest_point[1],
    color="purple",
    label="Furthest Point",
    zorder=5,
)

# Draw circles for the closest and furthest distances
circle_closest = plt.Circle(
    (cx, cy),
    min_distance,
    color="green",
    fill=False,
    linestyle="--",
    label="Closest Radius",
)
circle_furthest = plt.Circle(
    (cx, cy),
    max_distance,
    color="purple",
    fill=False,
    linestyle="--",
    label="Furthest Radius",
)
plt.gca().add_artist(circle_closest)
plt.gca().add_artist(circle_furthest)

# Annotate the plot
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Polygon, Center of Mass, and Radii")
plt.legend(loc="upper left")
plt.axis("equal")
plt.show()

# Print the results
print(f"Area: {area:.2f}")
print(f"Center of Mass: ({cx:.2f}, {cy:.2f})")
print(
    f"Closest Point: ({closest_point[0]:.2f}, {closest_point[1]:.2f}) with Distance: {min_distance:.2f}"
)
print(
    f"Furthest Point: ({furthest_point[0]:.2f}, {furthest_point[1]:.2f}) with Distance: {max_distance:.2f}"
)
print(f"Roundness(Max-min): {max_distance-min_distance:.2f}")
print(f"Roundness RMS: {rms:.2f}")
print(f"Average Radius: {np.mean(distances)}")
print(f"Perimeter: {perimeter}")
