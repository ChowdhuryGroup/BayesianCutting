import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os
from scipy.interpolate import splprep, splev

trial = 58
dir = f"/Users/conradkuz/Library/CloudStorage/OneDrive-SharedLibraries-TheOhioStateUniversity/Chowdhury Lab (ALL) - Documents/Lab Files/BayesianGlassCutting/2025-04-29/trial images/trial {trial}"
print(dir)
print(os.listdir(dir))


def shoelaceArea(xs, ys):
    # Computes area of shape enclosed by list of xs and ys
    # Calculate the area using the Shoelace formula
    area = 0.5 * np.abs(np.dot(xs, np.roll(ys, 1)) - np.dot(ys, np.roll(xs, 1)))
    return area


def shoelaceCentroid(xs, ys):
    # Computes the center coordinate of a shape enclosed by list of xs and ys
    # Correct centroid calculation using the Shoelace formula
    area = shoelaceArea(xs, ys)
    cx = np.abs(
        (1 / (6 * area))
        * np.sum((xs + np.roll(xs, 1)) * (xs * np.roll(ys, 1) - np.roll(xs, 1) * ys))
    )
    cy = np.abs(
        (1 / (6 * area))
        * np.sum((ys + np.roll(ys, 1)) * (xs * np.roll(ys, 1) - np.roll(xs, 1) * ys))
    )
    return cx, cy


print("Area    Perimeter   Average Radius")
for filename in sorted(os.listdir(dir)):
    if filename.endswith(".txt"):
        # Load points from the file
        file_path = os.path.join(dir, filename)  # Replace with the correct path
        points = np.loadtxt(file_path)

        # Ensure the loop is closed by appending the first point to the end
        if not np.allclose(points[0], points[-1]):
            points = np.vstack([points, points[0]])

        # Separate x and y coordinates
        x_coords = points[:, 0]
        y_coords = points[:, 1]

        # Fit a spline through the points
        tck, u = splprep([x_coords, y_coords], s=1)  # 's' controls smoothing

        # Generate finer resolution points
        u_fine = np.linspace(0, 1, 250)  # Increase resolution
        x_smooth, y_smooth = splev(u_fine, tck)

        x_rough, y_rough = x_coords, y_coords

        area_rough = shoelaceArea(x_rough, y_rough)
        area_smooth = shoelaceArea(x_smooth, y_smooth)

        xcenter_rough, ycenter_rough = shoelaceCentroid(x_rough, y_rough)
        xcenter_smooth, ycenter_smooth = shoelaceCentroid(x_smooth, y_smooth)

        centroid_rough = np.array([xcenter_rough, ycenter_rough])
        centroid_smooth = np.array([xcenter_smooth, ycenter_smooth])

        # Calculate distances from the centroid to each point
        distances_rough = np.sqrt(
            (x_rough - xcenter_rough) ** 2 + (y_rough - ycenter_rough) ** 2
        )
        distances_smooth = np.sqrt(
            (x_smooth - xcenter_smooth) ** 2 + (y_smooth - ycenter_smooth) ** 2
        )
        distances = distances_smooth
        # Find the closest and furthest points
        min_distance = np.min(distances)
        max_distance = np.max(distances)
        closest_point = np.array(
            [x_smooth[np.argmin(distances)], y_smooth[np.argmin(distances)]]
        )
        furthest_point = np.array(
            [x_smooth[np.argmax(distances)], y_smooth[np.argmax(distances)]]
        )
        rms = np.sqrt(np.mean((distances - np.mean(distances)) ** 2))
        perimeter = np.sum(np.sqrt(np.diff(x_smooth) ** 2 + np.diff(y_smooth) ** 2))

        print(
            f"{shoelaceArea(x_smooth,y_smooth)}\t {perimeter} \t {np.mean(distances)}"
        )

        plt.figure(figsize=(10, 10))

        # Plot rough boundary with smaller markers
        plt.plot(
            x_rough, y_rough, "ko-", markersize=2, alpha=0.5, label="Rough Boundary"
        )

        # Plot smoothed boundary
        plt.plot(x_smooth, y_smooth, "r-", linewidth=1.5, label="Smoothed Boundary")

        # Plot centroid
        plt.scatter(
            xcenter_smooth,
            ycenter_smooth,
            color="red",
            label="Smoothed Centroid",
            zorder=5,
        )

        # Corrected closest and furthest points from the smoothed boundary
        closest_point = np.array(
            [x_smooth[np.argmin(distances)], y_smooth[np.argmin(distances)]]
        )
        furthest_point = np.array(
            [x_smooth[np.argmax(distances)], y_smooth[np.argmax(distances)]]
        )

        plt.scatter(
            closest_point[0],
            closest_point[1],
            color="green",
            label="Closest Point",
            zorder=5,
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
            (xcenter_smooth, ycenter_smooth),
            min_distance,
            color="green",
            fill=False,
            linestyle="--",
            label="Closest Radius",
        )
        circle_furthest = plt.Circle(
            (xcenter_smooth, ycenter_smooth),
            max_distance,
            color="purple",
            fill=False,
            linestyle="--",
            label="Furthest Radius",
        )

        plt.gca().add_artist(circle_closest)
        plt.gca().add_artist(circle_furthest)

        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Comparison: Rough vs. Smoothed Boundary")
        plt.legend(loc="upper left")
        plt.axis("equal")
        plt.show()
