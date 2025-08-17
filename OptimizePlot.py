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
from scipy.interpolate import interp1d


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


# %% function to onvert the compressor settings to pulse durations
# Load the CSV, from 2025-05-15 autocorrelator data
data = np.loadtxt("compressor vs pulse duration pharos.txt", delimiter=",", skiprows=1)
compressor_settings = data[:, 0]
autocorrelator_pulse_durations = data[:, 1]
pulse_durations_negatives = autocorrelator_pulse_durations
pulse_durations_negatives[
    compressor_settings < compressor_settings[np.argmin(autocorrelator_pulse_durations)]
] *= (
    -1
)  # Set pulse durations to - for compressor settings below the minimum pulse duration, representing negative chirp

# Create interpolation function: maps pulse_duration → compressor_setting
# This inverts the axis for interpolation
pulse_duration_from_compressor = interp1d(
    compressor_settings, pulse_durations_negatives, fill_value="extrapolate"
)  # Returns fs


# %% Convert our compressor settings to pulse durations, convert pulse picker to rep rate, convert focal position to our zero point, and convert energy in J to uJ
# Convert list of lists to NumPy array
initial_parameters = np.array(initial_parameters)

# Extract compressor settings (last column)
compressor_vals = initial_parameters[:, -1]
print(initial_parameters[:, -1])
# Interpolate to get pulse durations
pulse_durations = pulse_duration_from_compressor(compressor_vals)

# Replace last column with pulse durations
initial_parameters[:, -1] = pulse_durations
print(initial_parameters[:, -1])

initial_parameters[:, 0] *= 1e6  # Convert energy from J to uJ
initial_parameters[:, 2] -= 17  # Convert focal position to our zero point (17 mm).
initial_parameters[:, 1] = (
    20000 / initial_parameters[:, 1]
)  # Convert pulse picker to rep rate (kHz)
# convert hatch spacing to µm
initial_parameters[:, 4] *= 1e3  # Convert hatch spacing from mm to µm

# %%
# Lets create a grid of graphs
param_names = [
    "Pulse Energy",
    "Repetition Rate",
    "Focal Position",
    "Scan Speed",
    "Hatch Spacing",
    "Repeats",
    "Pulse Duration",
]

param_y_labels = [
    "Energy (µJ)",
    "Repetition Rate (Hz)",
    "Focal Position (mm)",
    "Scan Speed (mm/s)",
    "Hatch Spacing (µm)",
    "Repeats",
    "Pulse Duration (fs)",
]

objective = -np.array(tested_quality_factors)
cumulative_min = np.maximum.accumulate(objective)
num_params = len(param_names)
vline_index = np.argmax(objective)  # Index of the best objective value

# Plotting
fig, axes = plt.subplots(3, 3, figsize=(15, 10), sharex=True)
axes = axes.flatten()

# Objective function
axes[0].plot(objective, "k.-", linewidth=2, markersize=11)
axes[0].set_title("Objective Function", fontsize=20)
# axes[0].set_xlabel("Observation No.", fontweight="bold")
axes[0].set_ylabel("Objective", fontweight="bold", fontsize=14)
axes[0].axvline(vline_index, linestyle="--", color="k")

# Cumulative optimum
axes[1].plot(cumulative_min, "r.-", linewidth=2, markersize=11)
axes[1].set_title("Cumulative Optimum", fontsize=20)
# axes[1].set_xlabel("Observation No.", fontweight="bold")
axes[1].set_ylabel("Best Objective", fontweight="bold", fontsize=14)
axes[1].axvline(vline_index, linestyle="--", color="k")
colors = plt.cm.tab10.colors
# Parameter evolution
for i in range(num_params):
    axes[i + 2].plot(
        np.array(initial_parameters)[:, i],
        ".-",
        color=colors[i % len(colors)],
        linewidth=2,
        markersize=11,
    )
    axes[i + 2].set_title(param_names[i], fontsize=20)
    # axes[i + 2].set_xlabel("Observation No.", fontweight="bold")
    axes[i + 2].set_ylabel(param_y_labels[i], fontweight="bold", fontsize=14)
    axes[i + 2].axvline(vline_index, linestyle="--", color="k")

for i in [6, 7, 8]:
    axes[i].set_xlabel("Observation No.", fontweight="bold", fontsize=16)


plt.tight_layout()
plt.show()

# %%
# Plot parameter vs objective function
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()
colors = plt.cm.tab10.colors
for i in range(num_params):
    axis = i  # Default axis index
    # do not plot repetition rate
    if i == 1:
        continue
    if i > 1:
        axis = i - 1  # Adjust index for the axes array
    axes[axis].plot(
        np.array(initial_parameters)[:, i],
        objective,
        ".",
        color=colors[i + 2 % len(colors)],
        markersize=13,
    )
    axes[axis].set_title(param_names[i], fontsize=20)
    axes[axis].set_xlabel(param_y_labels[i], fontweight="bold", fontsize=16)
    # set y label to "Objective Function" only for the left 2 graphs
    if axis % 3 == 0:
        axes[axis].set_ylabel("Objective Function", fontweight="bold", fontsize=16)

plt.tight_layout()
plt.show()
# %%
# Get pulse duration of best cut
print(initial_parameters[:, -1][np.argmax(objective)])
# %%
print(
    "pulse duration of 149214 for trial 55.1:", pulse_duration_from_compressor(149214)
)
print("pulse duration of 30986 for trial 50:", pulse_duration_from_compressor(30986))

# %%
# plot matrix of objectives
plot_objective(optimizer.get_result())
# %%
