# Author: Conrad Kuz - kuz.1@osu.edu
# Date: 2023-09-07

import cv2
import numpy as np
from matplotlib import pyplot as plt
import os
from scipy import ndimage

# Run this in at a directory with images of bessel beam along propogation direction. (right now in mm) e.g. 4.60.tif, 4.55.tif,4.50.tif etc.

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
FIRST_IMAGE_POSITION = 0  # 17.2
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


# normalize lineouts
lineouts = lineouts / (np.max(lineouts))

yVals = np.linspace(0, lineoutLength, num=lineoutLength + 1) * micronPerPixel


[X, Y] = np.meshgrid(imageNames, yVals)

fig, ax = plt.subplots(1, 1)


# plots filled contour plot
# lineouts is smoothed with gaussian
graph = ax.pcolormesh(
    X,
    Y,
    ndimage.gaussian_filter(np.transpose(lineouts), sigma=0.8, order=0),
    shading="gouraud",
    cmap="jet",
)
graph.set_clim(0, 1)
# cbar = fig.colorbar(graph, shrink=0.75, label="Relative Intensity")
# cbar.ax.set_ylabel(["0","0.25","Relative Intensity","0.75","1"])

cbar = fig.colorbar(graph, shrink=0.75, label="Relative Intensity")
cbar.set_ticks([0, 0.25, 0.5, 0.75, 1])

ax.set_title("Bessel Beam Intensity Distribution")
ax.set_xlabel("Propogation Distance (mm)")
ax.set_ylabel("Width (µm)")
# ax.set_xlim(0, 2)

plt.show()
