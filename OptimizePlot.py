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
import matplotlib as mpl
from sklearn.metrics import r2_score
#from IPython.display import set_matplotlib_formats
%matplotlib inline
%config InlineBackend.figure_formats = ['svg']
# set plot font to arial
mpl.rcParams["font.family"] = "Arial"
# --- Publication Quality Settings ---
mpl.rcParams["font.family"] = "Arial"
mpl.rcParams["font.weight"] = "bold"        # Bold text everywhere
mpl.rcParams["axes.labelweight"] = "bold"   # Bold axis labels
mpl.rcParams["axes.titleweight"] = "bold"   # Bold titles

# Font Sizes
mpl.rcParams["font.size"] = 14              # Base font size
mpl.rcParams["axes.titlesize"] = 20         # Title font size
mpl.rcParams["axes.labelsize"] = 16         # Axis label font size
mpl.rcParams["xtick.labelsize"] = 14        # X-tick label size
mpl.rcParams["ytick.labelsize"] = 14        # Y-tick label size

# Thicker Lines and Ticks for better visibility
mpl.rcParams["axes.linewidth"] = 2          # Thicker subplot borders (spines)
mpl.rcParams["xtick.major.width"] = 2       # Thicker x-ticks
mpl.rcParams["xtick.major.size"] = 6        # Longer x-ticks
mpl.rcParams["ytick.major.width"] = 2       # Thicker y-ticks
mpl.rcParams["ytick.major.size"] = 6        # Longer y-ticks


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
quality_standard_deviation = []

for trialNumber in range(0, len(parameterSheet)):
    initial_parameters.append(list(parameterSheet[trialNumber, 2 : len(space) + 2]))
    initial_quality_factors.append(parameterSheet[trialNumber, len(space) + 2])
    quality_standard_deviation.append(
        parameterSheet[trialNumber, len(space) + 3]
    )

print("NUMBER OF TRIALS: ", len(initial_parameters))
print("Input Parameters: ", initial_parameters)
print("Quality Parameters: ", initial_quality_factors)
print("Quality Standard Deviation: ", quality_standard_deviation)

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
compressor_vals_mm = initial_parameters[:, -1]
print("Compressor Vals",initial_parameters[:, -1])
# Interpolate to get pulse durations
pulse_durations = pulse_duration_from_compressor(compressor_vals_mm)


tau_min = np.min(np.abs(pulse_durations))  # Transform-limited duration in fs
print("Minimum Pulse Duration (fs):", tau_min)
# Calculate magnitude of GDD in fs^2
# Note: This assumes pulse_durations >= tau_min. 
# If your data has noise making tau < 300, clip it or handle NaNs.
gdd_values = np.sign(pulse_durations)*(tau_min**2 / (4 * np.log(2))) * np.sqrt((np.abs(pulse_durations) / tau_min)**2 - 1)

# Replace last column with pulse durations
#initial_parameters[:, -1] = pulse_durations
#add pulse durations as new last column
initial_parameters = np.column_stack((initial_parameters[:,:-1], pulse_durations,compressor_vals_mm,gdd_values))
print(initial_parameters[:, -1])

initial_parameters[:, 0] *= 1e6  # Convert energy from J to uJ
initial_parameters[:, 2] -= 17  # Convert focal position to our zero point (17 mm).
initial_parameters[:, 1] = (
    20 / initial_parameters[:, 1]
)  # Convert pulse picker to rep rate (kHz)
# convert hatch spacing to µm
initial_parameters[:, 4] *= 1e3  # Convert hatch spacing from mm to µm

#do the same conversion for space bounds
space[0].low *= 1e6
space[0].high *= 1e6
space[2].low -= 17
space[2].high -= 17
original_low = space[1].low
original_high = space[1].high
space[1].low = 20 / original_high
space[1].high = 20 / original_low
space[4].low *= 1e3
space[4].high *= 1e3

# %%
# Lets create a grid of graphs

param_names = [
    "Pulse Energy",
    "Repetition Rate",
    "Focal Position",
    "Scan Speed",
    "Hatch Spacing",
    "Repeats",
    "Pulse Chrip",
]

param_y_labels = [
    "Energy (µJ)",
    "Repetition Rate (kHz)",
    "Focal Position (mm)",
    "Scan Speed (mm/s)",
    "Hatch Spacing (µm)",
    "Repeats",
    "Chirp-Signed Pulse Duration (fs)",
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
#axes[0].set_title("Objective Function", fontsize=20)
# axes[0].set_xlabel("Observation No.", fontweight="bold")
axes[0].set_ylabel("Objective", fontweight="bold", fontsize=14)
axes[0].axvline(vline_index, linestyle="--", color="k")

# Cumulative optimum
axes[1].plot(cumulative_min, "r.-", linewidth=2, markersize=11)
#axes[1].set_title("Cumulative Optimum", fontsize=20)
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
    #axes[i + 2].set_title(param_names[i], fontsize=20)
    # axes[i + 2].set_xlabel("Observation No.", fontweight="bold")
    axes[i + 2].set_ylabel(param_y_labels[i], fontweight="bold", fontsize=14)
    axes[i + 2].axvline(vline_index, linestyle="--", color="k")
    if i == num_params - 1:
            # Create a twin axis that shares the x-axis
            ax2 = axes[i + 2].twinx()
            
            # 1. Sync the Y-limits so the 'canvas' matches Pulse Duration exactly
            ax2.set_ylim(axes[i + 2].get_ylim())
            
            # 2. Get GDD values (from the last column we added: index 8)
            # We use these only to determine the min/max for the tick range
            current_gdd_vals = initial_parameters[:, -1]
            
            # 3. Create 5 evenly spaced GDD ticks for the label
            gdd_ticks = np.linspace(current_gdd_vals.min(), current_gdd_vals.max(), 5)

            # 4. Calculate where these GDD ticks fall on the Pulse Duration (Y) scale
            # Formula: tau = tau_min * sqrt(1 + (beta * gdd)^2) where beta = 4ln2/tau_min^2
            # Note: We use absolute value of GDD because +GDD and -GDD result in the same duration
            tick_locs = np.sign(gdd_ticks)*tau_min * np.sqrt(1 + (np.abs(gdd_ticks) * (4 * np.log(2)) / tau_min**2)**2)

            # 5. Manually set the ticks and labels on the right axis
            ax2.set_yticks(tick_locs)
            # Format the labels (e.g., 0, 5000, 10000)
            #ax2.set_yticklabels([f"{v:.0f}" for v in gdd_ticks])
            ax2.set_yticklabels([f"{v:.1e}".replace("e+0","e") for v in gdd_ticks])
            ax2.set_ylabel("GDD ($fs^2$)", fontweight="bold", fontsize=14)

for i in [6, 7, 8]:
    axes[i].set_xlabel("Trial", fontweight="bold", fontsize=16)
    axes[i].set_xticks(range(0, len(objective)+1, 10))
#Add a,b,c... to the top left of each subplot
labels = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
for ax, label in zip(axes, labels):
    ax.text(
        0.02,
        0.93,
        label,
        transform=ax.transAxes,
        fontsize=25,
        fontweight="bold",
        va="top",
        ha="left",
    )

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
    #axes[axis].set_title(param_names[i], fontsize=20)
    axes[axis].set_xlabel(param_y_labels[i], fontweight="bold", fontsize=16)
    # set y label to "Objective Function" only for the left 2 graphs
    if axis % 3 == 0:
        axes[axis].set_ylabel("Objective Function", fontweight="bold", fontsize=16)
    if i == num_params - 1:
        # Create a twin axis that shares the x-axis
        ax2 = axes[axis].twiny()
        
        # 1. Sync the Y-limits so the 'canvas' matches Pulse Duration exactly
        ax2.set_xlim(axes[axis].get_ylim())
        
        # 2. Get GDD values (from the last column we added: index 8)
        # We use these only to determine the min/max for the tick range
        current_gdd_vals = initial_parameters[:, -1]
        
        # 3. Create 5 evenly spaced GDD ticks for the label
        gdd_ticks = np.linspace(current_gdd_vals.min(), current_gdd_vals.max(), 5)

        # 4. Calculate where these GDD ticks fall on the Pulse Duration (Y) scale
        # Formula: tau = tau_min * sqrt(1 + (beta * gdd)^2) where beta = 4ln2/tau_min^2
        # Note: We use absolute value of GDD because +GDD and -GDD result in the same duration
        tick_locs = np.sign(gdd_ticks)*tau_min * np.sqrt(1 + (np.abs(gdd_ticks) * (4 * np.log(2)) / tau_min**2)**2)

        # 5. Manually set the ticks and labels on the right axis
        ax2.set_xticks(tick_locs)
        # Format the labels (e.g., 0, 5000, 10000)
        #ax2.set_yticklabels([f"{v:.0f}" for v in gdd_ticks])
        ax2.set_xticklabels([f"{v:.1e}".replace("e+0","e") for v in gdd_ticks])
        ax2.set_xlabel("GDD ($fs^2$)", fontweight="bold", fontsize=14)
#Add a,b,c... to the top left of each subplot
labels = ["a", "b", "c", "d", "e", "f"]
for ax, label in zip(axes, labels):
    ax.text(
        0.02,
        0.93,
        label,
        transform=ax.transAxes,
        fontsize=25,
        fontweight="bold",
        va="top",
        ha="left",
    )
plt.tight_layout()
plt.show()

# %% ---------------------------------------
# PARALLEL COORDINATES: Fixed Scaling & Columns
# ---------------------------------------
import pandas as pd

import matplotlib.colors as mcolors

# 1. Setup Data Frame
# Re-create the full column list based on your code
base_cols = [dim.name for dim in space] 
extra_cols = ["Pulse Duration (fs)", "Compressor Pos (mm)", "GDD"] 
all_cols = base_cols + extra_cols[:initial_parameters.shape[1] - len(base_cols)]

df = pd.DataFrame(initial_parameters, columns=all_cols)
df['Quality'] = initial_quality_factors

# --- FILTERING COLUMNS ---
# Remove redundant columns to unclutter the plot.
# e.g., We likely don't need 'Compressor Setting' (int) AND 'Compressor Pos' (mm) AND 'Pulse Duration'.
# Let's keep just the PHYSICAL parameters.
cols_to_plot = [
    'Pulse Energy', 
    'FocalPosition', 
    'scan_speed', 
    'HatchSpacing', 
    'Repeats', 
    'Pulse Duration (fs)', # Prefer this over raw compressor settings
    # 'GDD'                # Optional: Add if GDD is distinct enough
]

# Ensure we only try to plot columns that actually exist
cols_to_plot = [c for c in cols_to_plot if c in df.columns]
df_plot = df[cols_to_plot].copy()

# 2. Normalize Data (Min-Max Scaling)
# This fits everything into the 0-1 range for the plot lines
df_norm = (df_plot - df_plot.min()) / (df_plot.max() - df_plot.min())

# 3. Setup Plot
fig, ax = plt.subplots(figsize=(15, 6))

# --- COLOR SCALE FIX ---
# Your previous plot was all yellow because LogNorm compressed the high values.
# Linear is better here if most of your data is "decent".
# We set vmin to 0.0 (or the minimum quality) and vmax to 1.0.
cmap = plt.get_cmap('viridis') 
norm = plt.Normalize(vmin=df['Quality'].min(), vmax=df['Quality'].max())

# 4. Plot Lines
# We sort by Quality so the best (yellow) lines are drawn ON TOP of the bad (purple) lines
sorted_indices = df['Quality'].argsort()

for i in sorted_indices:
    # Get normalized Y values for the parameters
    y_vals = df_norm.iloc[i].values
    q_val = df.iloc[i]['Quality']
    
    # Plot
    ax.plot(
        range(len(cols_to_plot)), 
        y_vals, 
        color=cmap(norm(q_val)), 
        alpha=0.7,          # Transparency helps see density
        linewidth=1.5
    )

# 5. Add Real Value Labels
for idx, col in enumerate(cols_to_plot):
    min_orig = df[col].min()
    max_orig = df[col].max()
    
    # Axis ticks (Top/Bottom)
    ax.text(idx, -0.05, f"{min_orig:.3g}", ha='center', fontsize=10, color='gray')
    ax.text(idx, 1.05, f"{max_orig:.3g}", ha='center', fontsize=10, fontweight='bold')
    
    # Column Header
    ax.text(idx, 1.1, col, ha='center', fontsize=11, fontweight='bold', rotation=15)
    
    # Vertical grid line
    ax.axvline(idx, color='gray', linestyle=':', alpha=0.3)

# 6. Clean up Axes
ax.set_xticks([])
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)

# 7. Add Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, pad=0.02)
cbar.set_label('Quality Factor', rotation=270, labelpad=20, fontsize=12)

plt.title(f"Parallel Coordinates: Physical Parameters (n={len(df)})", fontsize=16, y=1.15)
plt.show()
#%%
#Basin of attraction plot

#calculate the euclidean distance from each point to the best point after normalizing each parameter to 0-1 range
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
normalized_parameters = scaler.fit_transform(initial_parameters[:, :-2])  # Exclude last two columns (compressor and GDD) from normalization
best_index = np.argmax(objective)
distances = np.linalg.norm(normalized_parameters - normalized_parameters[best_index], axis=1)
plt.figure(figsize=(8,6))
plt.plot(distances, objective, "bo", markersize=10)
plt.xlabel("Euclidean Distance from Best Point (Normalized)", fontweight="bold", fontsize=16)
plt.ylabel("Objective Function", fontweight="bold", fontsize=16)
plt.title("Basin of Attraction", fontsize=20)
plt.grid(True)
plt.show()

#do the same but with numpy for scaling
for i in range(initial_parameters.shape[1]-2):
    min_val = space[i].low
    max_val = space[i].high
    #print min max of space and initial parameters
    print("min",param_names[i],min_val,np.min(initial_parameters[:, i]))
    print("max",param_names[i],max_val,np.max(initial_parameters[:, i]))
    normalized_parameters[:, i] = (initial_parameters[:, i] - min_val) / (max_val - min_val)
    #for compressor setting
    if i == initial_parameters.shape[1]-3:
        min_val = 1000
        max_val = 200000
        print("Compressor Setting min", min_val, np.min(initial_parameters[:, i+1]))
        print("Compressor Setting max", max_val, np.max(initial_parameters[:, i+1]))
        normalized_parameters[:, i] = (initial_parameters[:, i+1] - min_val) / (max_val - min_val)
distances = np.linalg.norm(normalized_parameters - normalized_parameters[best_index], axis=1)
plt.figure(figsize=(8,6))
plt.plot(distances, objective, "bo", markersize=10)
plt.xlabel("Euclidean Distance from Best Point (Normalized)", fontweight="bold", fontsize=16)
plt.ylabel("Objective Function", fontweight="bold", fontsize=16)
plt.title("Basin of Attraction (Manual Normalization)", fontsize=20)
plt.grid(True)
plt.show()

#%%
#basin of attraction nice
# set plot font to arial
mpl.rcParams["font.family"] = "Arial"
# --- Publication Quality Settings ---
mpl.rcParams["font.family"] = "Arial"
mpl.rcParams["font.weight"] = "bold"        # Bold text everywhere
mpl.rcParams["axes.labelweight"] = "bold"   # Bold axis labels
mpl.rcParams["axes.titleweight"] = "bold"   # Bold titles

# Font Sizes
mpl.rcParams["font.size"] = 14              # Base font size
mpl.rcParams["axes.titlesize"] = 20         # Title font size
mpl.rcParams["axes.labelsize"] = 16         # Axis label font size
mpl.rcParams["xtick.labelsize"] = 14        # X-tick label size
mpl.rcParams["ytick.labelsize"] = 14        # Y-tick label size

# Thicker Lines and Ticks for better visibility
mpl.rcParams["axes.linewidth"] = 2          # Thicker subplot borders (spines)
mpl.rcParams["xtick.major.width"] = 2       # Thicker x-ticks
mpl.rcParams["xtick.major.size"] = 6        # Longer x-ticks
mpl.rcParams["ytick.major.width"] = 2       # Thicker y-ticks
mpl.rcParams["ytick.major.size"] = 6        # Longer y-ticks
# 1. SETUP: Create two subplots sharing the X-axis
# height_ratios=[3, 1] means the top plot (detail) gets 3x more space than the bottom
fig, (ax_top, ax_bottom) = plt.subplots(2, 1, sharex=True, figsize=(10, 7),
                                        gridspec_kw={'height_ratios': [6, 1], 'hspace': 0.07})

# 2. PLOT DATA ON BOTH AXES
# We assume 'distances' and 'objective' are defined from your previous steps
trials = np.arange(len(objective))

# Plot on Top (The "Good" Data)
sc1 = ax_top.scatter(distances, objective, c=trials, cmap='viridis', s=100, alpha=0.9, edgecolors='k', linewidth=0.5)
# Plot on Bottom (The "Bad" Data)
sc2 = ax_bottom.scatter(distances, objective, c=trials, cmap='viridis', s=100, alpha=0.9, edgecolors='k', linewidth=0.5)

# 3. SET LIMITS (The "Custom Scale" Magic)
# Top plot: Focuses on the trend (e.g., 0.4 to 0.95)
ax_top.set_ylim(0.4, 0.95)  
# Bottom plot: Focuses on the failures (e.g., -0.05 to 0.1)
ax_bottom.set_ylim(-0.05, 0.08)  

# 4. REMOVE BORDERS TO CREATE "BREAK" EFFECT
ax_top.spines['bottom'].set_visible(False)
ax_bottom.spines['top'].set_visible(False)
ax_top.xaxis.tick_top()
ax_top.tick_params(labeltop=False)  # Don't put tick labels at the very top
ax_bottom.xaxis.tick_bottom()
#set y axis bottom ticks to 0 and .08
ax_bottom.yaxis.set_ticks([0, 0.08])
# 5. ADD DIAGONAL "BREAK" LINES (Optional but professional)
d = .01  # how big to make the diagonal lines in axes coordinates
kwargs = dict(transform=ax_top.transAxes, color='k', clip_on=False)
ax_top.plot((-d, +d), (-d, +d), **kwargs)        # Top-left diagonal
ax_top.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # Top-right diagonal

kwargs.update(transform=ax_bottom.transAxes)  # Switch to bottom axes
ax_bottom.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # Bottom-left diagonal
ax_bottom.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # Bottom-right diagonal

# 6. LABELS & GRIDS
ax_top.grid(True, linestyle='--', alpha=0.6)
ax_bottom.grid(True, linestyle='--', alpha=0.6)

ax_bottom.set_xlabel("Norm. Euclidean Distance from Best Point", fontsize=14, weight='bold')
# Put the Y-label in the "middle" of the figure explicitly
fig.text(0.04, 0.5, 'Objective Function', va='center', rotation='vertical', fontsize=14, weight='bold')
#ax_top.set_title("Basin of Attraction: Convergence over Time", fontsize=18, weight='bold', pad=20)

#label 

# 7. COLORBAR
# We add it to the right of the whole figure
fig.subplots_adjust(right=0.85)
cbar_ax = fig.add_axes([0.88, 0.15, 0.03, 0.7]) # [left, bottom, width, height]
cbar = fig.colorbar(sc1, cax=cbar_ax)
cbar.set_label('Trial Number (Progression)', fontsize=12, weight='bold')

plt.show()

#%%
#plot standard deviation Y vs objective function X
#remove zeros from objective and quality_standard_deviation
valid_indices = [i for i in range(len(objective)) if quality_standard_deviation[i] > 0]
objective_zeroed = np.array([objective[i] for i in valid_indices])
quality_standard_deviation = np.array([quality_standard_deviation[i] for i in valid_indices])
plt.figure(figsize=(8,6))
plt.plot(objective_zeroed, quality_standard_deviation, "bo", markersize=10)
#create exponential fit line


# Fit to log-space: log(y) = mx + c
m, c = np.polyfit(objective_zeroed, np.log(quality_standard_deviation), 1)

# Generate fit and calculate R2
x_fit = np.linspace(min(objective_zeroed), max(objective_zeroed), 100)
y_fit = np.exp(m * x_fit + c)
r2 = r2_score(np.log(quality_standard_deviation), m * objective_zeroed + c)

# Plot with descriptive label
plt.plot(x_fit, y_fit, "r--", linewidth=2, 
         label=f"Exponential Fit: $y = {np.exp(c):.2f}e^{{{m:.2f}x}}$, $R^2 = {r2:.3f}$")
plt.legend()
plt.xlabel("Objective Function", fontweight="bold", fontsize=16)
plt.ylabel("Objective Standard Deviation", fontweight="bold", fontsize=16)
#plt.title("Quality Standard Deviation vs Objective Function", fontsize=20)
plt.grid(True)
plt.yscale("log")
#plt.xscale("log")
plt.xlim(0.0,1)
plt.show()


#%%
#combined std plot and basin of attraction plot
import matplotlib.gridspec as gridspec
# 1. PREPARE DATA FOR PLOT (B) (Remove zeros/invalid)
# 1. PREPARE DATA
# Assuming 'objective', 'distances', 'objective_zeroed', and 'quality_standard_deviation' are defined
obj_clean = objective_zeroed
std_clean = quality_standard_deviation
trials = np.arange(len(objective))

# 2. SETUP FIGURE WITH GRIDSPEC
# width_ratios=[1, 0.03, 0.22, 1] -> Spacer column increased to 0.22 to fit larger B-axis labels
fig = plt.figure(figsize=(16, 7))
gs = gridspec.GridSpec(2, 4, width_ratios=[1, 0.03, 0.25, 1], height_ratios=[6, 1], wspace=0.05, hspace=0.07)

# --- PART (A): BASIN OF ATTRACTION (Column 0) ---
ax_top = fig.add_subplot(gs[0, 0])
ax_bottom = fig.add_subplot(gs[1, 0], sharex=ax_top)

# Plot Data
sc1 = ax_top.scatter(distances, objective, c=trials, cmap='viridis', s=120, alpha=0.9, edgecolors='k', linewidth=0.5)
sc2 = ax_bottom.scatter(distances, objective, c=trials, cmap='viridis', s=120, alpha=0.9, edgecolors='k', linewidth=0.5)

# Limits & Breaks
ax_top.set_ylim(0.4, 0.95)
ax_bottom.set_ylim(-0.05, 0.08)
ax_top.spines['bottom'].set_visible(False)
ax_bottom.spines['top'].set_visible(False)
ax_top.xaxis.tick_top()
ax_top.tick_params(labeltop=False)
ax_bottom.xaxis.tick_bottom()
ax_bottom.yaxis.set_ticks([0, 0.08])

# Diagonal "Break" Lines
d = .015
kwargs = dict(transform=ax_top.transAxes, color='k', clip_on=False)
ax_top.plot((-d, +d), (-d, +d), **kwargs)
ax_top.plot((1 - d, 1 + d), (-d, +d), **kwargs)
kwargs.update(transform=ax_bottom.transAxes)
ax_bottom.plot((-d, +d), (1 - d, 1 + d), **kwargs)
ax_bottom.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

# Labels & Ticks (A)
ax_top.grid(True, linestyle='--', alpha=0.6)
ax_bottom.grid(True, linestyle='--', alpha=0.6)

# INCREASED FONT SIZES
ax_top.tick_params(axis='both', which='major', labelsize=16)
ax_bottom.tick_params(axis='both', which='major', labelsize=16)

ax_bottom.set_xlabel("Norm. Euclidean Distance from Best Point", fontsize=18, weight='bold')
# Adjusted x-position of Y-label (-0.15) to prevent overlap with larger tick numbers
ax_bottom.text(-0.15, 3.5, 'Objective Function', rotation='vertical', va='center', fontsize=18, weight='bold', transform=ax_bottom.transAxes)

# --- COLORBAR (Column 1) ---
cax = fig.add_subplot(gs[:, 1])
cbar = fig.colorbar(sc1, cax=cax)
cbar.set_label('Trial Number (Progression)', fontsize=16, weight='bold')
cbar.ax.tick_params(labelsize=14)

# --- PART (B): STD DEV (Column 3) ---
ax_std = fig.add_subplot(gs[:, 3]) 

ax_std.plot(obj_clean, std_clean, "bo", markersize=10, alpha=0.8)

# Exponential Fit
m, c = np.polyfit(obj_clean, np.log(std_clean), 1)
x_fit = np.linspace(min(obj_clean), max(obj_clean), 100)
y_fit = np.exp(m * x_fit + c)
r2 = r2_score(np.log(std_clean), m * obj_clean + c)

ax_std.plot(x_fit, y_fit, "r--", linewidth=2, 
         label=f"Fit: $y = {np.exp(c):.2f}e^{{{m:.2f}x}}$\n$R^2 = {r2:.3f}$")

# Labels & Ticks (B)
ax_std.legend(fontsize=14, loc='upper right')
ax_std.set_xlabel("Objective Function", fontweight="bold", fontsize=18)
ax_std.set_ylabel("Objective Standard Deviation", fontweight="bold", fontsize=18)
ax_std.tick_params(axis='both', which='major', labelsize=16)

# Grid Update: Major only
ax_std.grid(True, which="major", linestyle='--', alpha=0.6) 
ax_std.set_yscale("log")
ax_std.set_xlim(0.0, 1.0)

# --- ADD SUBPLOT LABELS (a) and (b) ---
# Increased to 24pt
ax_top.text(-0.12, 1.05, "(a)", transform=ax_top.transAxes, fontsize=24, fontweight='bold', va='top', ha='right')
ax_std.text(-0.12, 1.02, "(b)", transform=ax_std.transAxes, fontsize=24, fontweight='bold', va='top', ha='right')

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
# print pulse duration of compressor 1000 and 200000
print(
    "Pulse duration for compressor setting 1000:", pulse_duration_from_compressor(1000)
)
print(
    "Pulse duration for compressor setting 200000:",
    pulse_duration_from_compressor(200000),
)
# %%
