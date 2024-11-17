import cv2
import numpy as np
import matplotlib.pyplot as plt

#Something like this will work.

# Step 1: Load the image
image = cv2.imread('5x 1 deg (2).png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Step 2: Preprocess the image
_, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)  # Adjust threshold as needed

# Step 3: Detect contours
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
hole_contour = max(contours, key=cv2.contourArea)  # Assuming the hole is the largest contour
sorted_contours = sorted(contours, key=cv2.contourArea,reverse=True)
hole_contour = sorted_contours[0]   

# Step 4: Fit a circle and calculate roundness
(x, y), radius = cv2.minEnclosingCircle(hole_contour)
circle_area = np.pi * (radius ** 2)
contour_area = cv2.contourArea(hole_contour)
circularity = (4 * np.pi * contour_area) / (cv2.arcLength(hole_contour, True) ** 2)

# Step 5: Draw and visualize
output = image.copy()
cv2.drawContours(output, [hole_contour], -1, (0, 255, 0), 2)  # Contour
cv2.circle(output, (int(x), int(y)), int(radius), (255, 0, 0), 2)  # Fitted circle

plt.figure(figsize=(10, 10))
plt.imshow(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))
plt.title(f"Circularity: {circularity:.2f}")
plt.show()

# Step 1: Load and preprocess the image
image = cv2.imread('5x 1 deg (2).png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Detect the largest contour (hole)
_, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
hole_contour = max(contours, key=cv2.contourArea)

# Step 2: Get the center and radius of the hole
(x, y), radius = cv2.minEnclosingCircle(hole_contour)
center = (int(x), int(y))
hole_radius = int(radius)

# Step 3: Create a radial mask for the debris region
ring_start = int(hole_radius * 1.1)  # Start a bit outside the hole
ring_end = int(hole_radius * 2.0)   # Adjust outer limit as needed
rows, cols = gray.shape
y_grid, x_grid = np.ogrid[:rows, :cols]
distance_from_center = np.sqrt((x_grid - center[0])**2 + (y_grid - center[1])**2)

# Mask for the ring
ring_mask = (distance_from_center >= ring_start) & (distance_from_center <= ring_end)

# Step 4: Analyze intensity in the ring region
ring_values = gray[ring_mask]

# Compute a radial profile (average intensity at each radius)
radii = np.arange(ring_start, ring_end + 1)
intensity_profile = [
    gray[(distance_from_center >= r) & (distance_from_center < r + 1)].mean()
    for r in radii
]

# Step 5: Detect edges of the debris ring based on intensity
intensity_gradient = np.gradient(intensity_profile)
inner_edge_index = np.argmax(intensity_gradient)  # Sharp intensity increase
outer_edge_index = np.argmin(intensity_gradient)  # Sharp intensity decrease
ring_thickness = radii[outer_edge_index] - radii[inner_edge_index]

# Step 6: Plot the results
plt.figure(figsize=(10, 5))
plt.plot(radii, intensity_profile, label='Intensity Profile')
plt.axvline(radii[inner_edge_index], color='g', linestyle='--', label='Inner Edge')
plt.axvline(radii[outer_edge_index], color='r', linestyle='--', label='Outer Edge')
plt.title(f"Debris Ring Thickness: {ring_thickness:.2f} pixels")
plt.xlabel("Radius (pixels)")
plt.ylabel("Intensity")
plt.legend()
plt.show()