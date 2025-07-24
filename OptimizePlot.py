# %%
from skopt import Optimizer
from skopt.space import Real, Integer
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas
from skopt.plots import (
    plot_evaluations,
    plot_objective,
    plot_convergence,
    plot_gaussian_process,
)
import beamConstruct
import openpyxl
import os
import time


parameterFilepath = r"ImagesToTest/backupParameterMeasurement2025-04-29.xlsx"


# Define the parameter space min and max
space = [
    Real(0.000081, 0.000153, name="Pulse Energy"),  # Pulse energy (J)
    Integer(1, 8, name="PulsePicker"),
    Real(
        17.2, 20.1, name="FocalPosition"
    ),  # Position of slide (mm) with respect to bessel characterization
    Real(1, 250, name="scan_speed"),  # Software Scan speed (mm/s)
    Real(0.001, 0.01, name="HatchSpacing"),  # Spacing of hatch (m)
    Integer(0, 200, name="Repeats"),  # Number of times to repeat circle (unitless)
    Integer(1000, 200000, name="Compressor Setting"),  # Pharos Compressor Setting
]


parameterSheet = pandas.read_excel(
    parameterFilepath,
    sheet_name="Parameters",
).to_numpy()


initial_parameters = []
initial_quality_factors = []

for trialNumber in range(0, len(parameterSheet)):
    initial_parameters.append(list(parameterSheet[trialNumber, 2 : len(space) + 2]))
    initial_quality_factors.append(parameterSheet[trialNumber, len(space) + 2])

print("NUMBER OF TRIALS: ", len(initial_parameters))
print("Input Parameters: ", initial_parameters)
print("Quality Parameters: ", initial_quality_factors)


# Initialize the optimizer, this is where you set the optimizer strategies and such
optimizer = Optimizer(
    dimensions=space,
    random_state=0,
    # acq_func="PI",
    # acq_func_kwargs={"xi": 0.1},
)  # Set random_state to None for randomization of outputs, generate next suggested parameters with random_state=0,1,2

# Feed the initial data to the optimizer
for params, quality in zip(initial_parameters, initial_quality_factors):
    if quality == 0:
        quality = -00
    optimizer.tell(params, -quality)  # Negate quality factor since we are minimizing


tested_parameters = np.array(optimizer.Xi)
tested_quality_factors = np.array(optimizer.yi)

# %%

# Plot quality factor vs iteration
plt.figure(figsize=(8, 6))
plt.plot(
    range(1, len(tested_quality_factors) + 1),
    -tested_quality_factors,
    marker="o",
    label="Quality Factor",
)
plt.xlabel("Trial")
plt.ylabel("Quality Score (0-1)")
plt.title("Optimization Progress")
plt.show()


# Visualizing optimization process: https://scikit-optimize.github.io/stable/auto_examples/plots/visualizing-results.html#
# plot_evaluations(optimizer.get_result())
# plt.show()

# plot_objective(optimizer.get_result())
# plt.show()

plot_convergence(optimizer.get_result())
plt.show()

# %%
# Plot convergence with better labels
mins = np.array(
    [
        np.min(tested_quality_factors[: i + 1])
        for i in range(len(tested_quality_factors))
    ]
)

plt.plot(range(1, len(tested_quality_factors) + 1), -mins, marker="o", color="purple")
plt.xlabel("Trial", fontsize=16, fontweight="bold")
plt.ylabel("Best Quality Score (0-1)", fontsize=16, fontweight="bold")
plt.title(
    "Optimization Convergence",
    fontsize=20,
)
plt.xticks(
    fontsize=16,
)
plt.yticks(fontsize=16)
plt.tight_layout()
plt.grid(True)
plt.show()

# %%
# Lets create a grid of graphs
param_names = [
    "Pulse Energy",
    "Pulse Picker",
    "Focal Position",
    "Scan Speed",
    "Hatch Spacing",
    "Repeats",
    "Pulse Duration(CHANGE FROM COMPRESSOR)",
]

param_y_labels = [
    "Energy (J)",
    "Pulse Picker",
    "Focal Position (mm)",
    "Scan Speed (mm/s)",
    "Hatch Spacing (m)",
    "Repeats",
    "Pulse Duration (fs) (CHANGE FROM COMPRESSOR)",
]

objective = -np.array(tested_quality_factors)
cumulative_min = np.maximum.accumulate(objective)
num_params = len(param_names)
vline_index = np.argmax(objective)  # Index of the best objective value

# Plotting
fig, axes = plt.subplots(3, 3, figsize=(15, 10))
axes = axes.flatten()

# Objective function
axes[0].plot(objective, "k.-")
axes[0].set_title("Objective Function")
axes[0].set_xlabel("Observation No.", fontweight="bold")
axes[0].set_ylabel("Objective", fontweight="bold")
axes[0].axvline(vline_index, linestyle="--", color="k")

# Cumulative optimum
axes[1].plot(cumulative_min, "r.-")
axes[1].set_title("Cumulative Optimum")
axes[1].set_xlabel("Observation No.", fontweight="bold")
axes[1].set_ylabel("Best Objective", fontweight="bold")
axes[1].axvline(vline_index, linestyle="--", color="k")

# Parameter evolution
for i in range(num_params):
    axes[i + 2].plot(
        np.array(initial_parameters)[:, i], ".--", color=colors[i % len(colors)]
    )
    axes[i + 2].set_title(param_names[i])
    axes[i + 2].set_xlabel("Observation No.", fontweight="bold")
    axes[i + 2].set_ylabel(param_y_labels[i], fontweight="bold")
    axes[i + 2].axvline(vline_index, linestyle="--", color="k")

plt.tight_layout()
plt.show()

# %%
