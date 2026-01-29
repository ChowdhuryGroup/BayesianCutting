# %% Main load in
# Author: Conrad Kuz - kuz.1@osu.edu
# Date: 2023-09-07

import cv2
import numpy as np
from matplotlib import pyplot as plt
import os
from scipy import ndimage
import matplotlib as mpl

# %matplotlib inline


# Run this in at a directory with images of bessel beam along propogation direction. (right now in mm) e.g. 4.60.tif, 4.55.tif,4.50.tif etc.
# %config InlineBackend.figure_formats = ['svg']
imageDirectory = r"/Users/conradkuz/Library/CloudStorage/OneDrive-SharedLibraries-TheOhioStateUniversity/Chowdhury Lab (ALL) - Glass cutting - Glass cutting/BayesianGlassCutting/2025-04-29/bessel characterization"
imageDirectory = r"/Users/conradkuz/Library/CloudStorage/OneDrive-SharedLibraries-TheOhioStateUniversity/Chowdhury Lab (ALL) - Glass cutting - Glass cutting/BayesianGlassCutting/2025-02-25/bessel characterization"
lineoutLength = 300
micronPerPixel = 600 / 3324


def findPeakPixel(image1):
    max_row, max_col = np.where(image1 == np.max(image1))
    return max_row[0], max_col[0]


def avgLineout(image, centerx, centery, linewidth=70, linelength=76):
    lineout = []
    for x in range(centerx - int(linelength / 2), centerx + 1 + int(linelength / 2)):
        valsAlongY = []
        for y in range(centery - int(linewidth / 2), centery + 1 + int(linewidth / 2)):
            valsAlongY.append(image[y, x])
        lineout.append(np.average(valsAlongY))
    return lineout


# Sets orientation and zero point of images
FIRST_IMAGE_POSITION = 17  # 17.2
images = []
imageNames = []
lineouts = []
background = 0
print(sorted(os.listdir(imageDirectory)))
for x in sorted(os.listdir(imageDirectory)):
    if x.lower().startswith("bkg"):
        # -1 flag ensures 16bit readin
        background = cv2.imread(os.path.join(imageDirectory, x), -1)

for x in sorted(os.listdir(imageDirectory)):
    if not x.lower().startswith("bkg") and x.lower().endswith(
        (
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".gif",
            ".tif",
            ".tiff",
            ".webp",
            ".heic",
            ".svg",
        )
    ):
        print(x)
        image = cv2.imread(os.path.join(imageDirectory, x), -1)
        # not sure why i cant just do image-background for background subtraction
        image = cv2.subtract(image, background)
        yp, xp = findPeakPixel(image)
        lineout = avgLineout(image, xp, yp, linelength=lineoutLength)
        lineouts.append(lineout)
        # images.append(image)
        imageNames.append((float(os.path.splitext(x)[0]) - FIRST_IMAGE_POSITION))

print(imageNames)
# %% Make Plots

# 1. Normalize lineouts
lineouts = lineouts / (np.max(lineouts))

# 2. Transpose and Smooth FIRST so we know the final shape
# We do this before creating the grid to ensure dimensions match exactly.
# If lineouts is (56, 301), C will be (301, 56).
C = ndimage.gaussian_filter(np.transpose(lineouts), sigma=0.8, order=0)

# 3. Get shapes directly from the data (C)
# C.shape[0] is the Y-axis (Width/Height)
# C.shape[1] is the X-axis (Propagation steps)
num_y_points = C.shape[0]
num_x_points = C.shape[1]

# 4. Generate Grids to match C exactly
# Y-axis (Width)
yVals = np.linspace(0, num_y_points * micronPerPixel, num=num_y_points)

# X-axis (Propagation)
# Assuming 'imageNames' holds your Z-positions.
# We ensure it matches the data dimension.
if len(imageNames) != num_x_points:
    # Fallback if imageNames doesn't match: create a linspace based on the size
    print(
        f"Warning: imageNames length ({len(imageNames)}) mismatch with data ({num_x_points}). generating new X-axis."
    )
    xVals = np.linspace(0, 4, num=num_x_points)  # Assuming 0 to 4mm scan
else:
    xVals = imageNames

[X, Y] = np.meshgrid(xVals, yVals)

# 5. Global Plot Settings
mpl.rcParams["font.family"] = "Arial"
mpl.rcParams["font.size"] = 16
mpl.rcParams["axes.linewidth"] = 1.5
mpl.rcParams["xtick.major.width"] = 1.5
mpl.rcParams["ytick.major.width"] = 1.5
mpl.rcParams["xtick.direction"] = "out"
mpl.rcParams["ytick.direction"] = "out"

fig, ax = plt.subplots(1, 1, figsize=(7, 5), dpi=300)

# 6. Plot
graph = ax.pcolormesh(
    X, Y, C, shading="gouraud", cmap="turbo", vmin=0, vmax=1, rasterized=True
)

# 7. Labels
ax.set_xlabel("Propagation Distance (mm)", fontsize=16, fontweight="bold")
ax.set_ylabel("Width (µm)", fontsize=16, fontweight="bold")

# 8. Ticks
ax.tick_params(axis="both", which="major", labelsize=14)
ax.set_xlim(0, 4)

# 9. Colorbar
cbar = fig.colorbar(graph, ax=ax, shrink=0.8, pad=0.03)
cbar.set_ticks([0, 0.25, 0.5, 0.75, 1])
cbar.ax.tick_params(labelsize=14)
cbar.set_label("Relative Intensity", fontsize=16, rotation=270, labelpad=20)
# output to notebook as svg

plt.tight_layout()
plt.savefig("Bessel_Beam_Plot.svg", format="svg", bbox_inches="tight")
plt.show()
# %% Make Plots

# normalize lineouts
lineouts = lineouts / (np.max(lineouts))

yVals = np.linspace(0, lineoutLength, num=lineoutLength + 1) * micronPerPixel


[X, Y] = np.meshgrid(imageNames, yVals)

# set plot font to arial
mpl.rcParams["font.family"] = "Arial"

fig, ax = plt.subplots(1, 1)


# plots filled contour plot
# lineouts is smoothed with gaussian
graph = ax.pcolormesh(
    X,
    Y,
    ndimage.gaussian_filter(np.transpose(lineouts), sigma=0.8, order=0),
    shading="gouraud",
    cmap="turbo",
)
graph.set_clim(0, 1)
# cbar = fig.colorbar(graph, shrink=0.75, label="Relative Intensity")
# cbar.ax.set_ylabel(["0","0.25","Relative Intensity","0.75","1"])

cbar = fig.colorbar(graph, shrink=0.75, label="Relative Intensity")
cbar.set_ticks([0, 0.25, 0.5, 0.75, 1])
cbar.ax.set_ylabel("Relative Intensity", fontsize=14)
cbar.ax.tick_params(labelsize=14)

ax.set_title("Bessel Beam Intensity Distribution", fontsize=16)
ax.set_xlabel("Propogation Distance (mm)", fontsize=14)
ax.set_ylabel("Width (µm)", fontsize=14)

ax.tick_params(axis="both", which="major", labelsize=12)

ax.set_xlim(0, 4)
# set high dpi
fig.set_dpi(300)
plt.show()


# %%# Create a plot of a zeroth-order Bessel beam focus
# Create a grid of coordinates
from scipy.special import j0

x = np.linspace(-5, 5, 1000)
y = np.linspace(-5, 5, 1000)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2)

# Simulate a zeroth-order Bessel beam intensity profile
intensity = j0(R) ** 2

# Normalize intensity for better visualization
intensity /= intensity.max()

# Create the plot with transparent background
fig, ax = plt.subplots(figsize=(6, 6), dpi=300)
ax.axis("off")  # Hide axes
ax.set_aspect("equal")
plt.imshow(intensity, cmap="hot", extent=(-10, 10, -10, 10), alpha=1)

# Save the image with transparent background
# plt.savefig("bessel_beam_focus.png", transparent=True, bbox_inches='tight', pad_inches=0)


# %%
