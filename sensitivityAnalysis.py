# %%
import numpy as np
import pandas
from skopt import Optimizer

parameterFilepath = r"ImagesToTest/backupParameterMeasurement2025-04-29.xlsx"


parameterSheet = pandas.read_excel(
    parameterFilepath,
    sheet_name="Measurements",
).to_numpy()

print(parameterSheet[0])

# columns are:
#'Trial' 'HAZ Area' 'Clean Cut Area' 'Perimeter' 'Average Radius' 'Cracking present (0(no) or 1(yes))' 'Total Time for 4 circles'


def objectiveScore(
    HAZArea,
    cleanCutArea,
    perimeter,
    averageRadius,
    crackingPresent,
    totalTime,
    weights=None,
):
    # Define weights for each parameter
    if weights is None:
        weights = {
            "roundness": 0.4,
            "haz": 0.2,
            "radius_ablated": 0.2,
            "cracking": 0.2,
        }
    if totalTime > 350:
        return 0
    if any(v != v for v in [HAZArea, cleanCutArea, perimeter, averageRadius]):
        return 0.0
    desired_radius = 311.75
    roundnessScore = weights["roundness"] * (
        1 - 4 * np.pi * (cleanCutArea / perimeter**2)
    )
    hazScore = weights["haz"] * (HAZArea - cleanCutArea) / HAZArea
    radiusScore = (
        weights["radius_ablated"]
        * np.abs(desired_radius - averageRadius)
        / desired_radius
    )
    if cleanCutArea != 0.0:
        crackingScore = weights["cracking"] * crackingPresent
    else:
        crackingScore = 1 * weights["cracking"]
    # Calculate the score based on the parameters and their weights
    score = 1 - (roundnessScore + hazScore + radiusScore + crackingScore)
    return score


weights = {
    "roundness": 0,
    "haz": 0,
    "radius_ablated": 0,
    "cracking": 1,
}
# test objective score on first row of parameter sheet
for i in range(1, len(parameterSheet)):
    if 52 != parameterSheet[i][0]:
        continue
    print(
        "trial",
        parameterSheet[i][0],
        ":",
        objectiveScore(*parameterSheet[i][1:7], weights=weights),
    )
print(np.std([1, 1, 0, 0]))

# %%
import matplotlib.pyplot as plt
import matplotlib as mpl

# set plot font to arial
mpl.rcParams["font.family"] = "Arial"
# --- Publication Quality Settings ---
mpl.rcParams["font.family"] = "Arial"
mpl.rcParams["font.weight"] = "bold"  # Bold text everywhere
mpl.rcParams["axes.labelweight"] = "bold"  # Bold axis labels
mpl.rcParams["axes.titleweight"] = "bold"  # Bold titles

# Font Sizes
mpl.rcParams["font.size"] = 14  # Base font size
mpl.rcParams["axes.titlesize"] = 20  # Title font size
mpl.rcParams["axes.labelsize"] = 16  # Axis label font size
mpl.rcParams["xtick.labelsize"] = 14  # X-tick label size
mpl.rcParams["ytick.labelsize"] = 14  # Y-tick label size

# Thicker Lines and Ticks for better visibility
mpl.rcParams["axes.linewidth"] = 2  # Thicker subplot borders (spines)
mpl.rcParams["xtick.major.width"] = 2  # Thicker x-ticks
mpl.rcParams["xtick.major.size"] = 6  # Longer x-ticks
mpl.rcParams["ytick.major.width"] = 2  # Thicker y-ticks
mpl.rcParams["ytick.major.size"] = 6  # Longer y-ticks
# sublot of 3 graphs of trial vs haz, isoperimetricratio, and radius with cracking as color
df = pandas.read_excel(parameterFilepath, sheet_name="Measurements", skiprows=1)

# drop the last 4 rows which are trial 55.1
df = df[:-4]
print(df.tail())
# 4 measurements per trial, so calculate haz ratio, isoperimetric ratio, and average radius per trial
df["haz_ratio"] = (df["HAZ Area"] - df["Clean Cut Area"]) / df["HAZ Area"]
df["isoperimetric_ratio"] = 4 * np.pi * df["Clean Cut Area"] / df["Perimeter"] ** 2
df["average_radius_"] = df["Average Radius"] / 2.494  # convert pixels to microns

# group by trial and calculate the mean and std
trial_summary = (
    df.groupby("Trial")
    .agg(
        {
            "haz_ratio": ["mean", "std"],
            "isoperimetric_ratio": ["mean", "std"],
            "average_radius_": ["mean", "std"],
            "Cracking present (0(no) or 1(yes))": ["mean"],
        }
    )
    .reset_index()
)
trial_summary.columns = [
    "Trial",
    "haz_ratio_mean",
    "haz_ratio_std",
    "isoperimetric_ratio_mean",
    "isoperimetric_ratio_std",
    "average_radius_mean",
    "average_radius_std",
    "cracking_mean",
]

# plot trial vs haz, isoperimetric ratio, and radius with cracking as color
fig, axs = plt.subplots(1, 3, figsize=(18, 5))
axs[0].errorbar(
    trial_summary["Trial"],
    trial_summary["haz_ratio_mean"],
    yerr=trial_summary["haz_ratio_std"],
    fmt="o",
    color="blue",
    ecolor="lightblue",
    elinewidth=2,
    capsize=3,
)
axs[0].set_title("Trial vs HAZ")
axs[0].set_xlabel("Trial")
axs[0].set_ylabel("Normalized HAZ Ratio")
axs[1].errorbar(
    trial_summary["Trial"],
    trial_summary["isoperimetric_ratio_mean"],
    yerr=trial_summary["isoperimetric_ratio_std"],
    fmt="o",
    color="green",
    ecolor="lightgreen",
    elinewidth=2,
    capsize=3,
)
axs[1].set_title("Trial vs Isoperimetric Ratio")
axs[1].set_xlabel("Trial")
axs[1].set_ylabel("Isoperimetric Ratio")
axs[2].errorbar(
    trial_summary["Trial"],
    trial_summary["average_radius_mean"],
    yerr=trial_summary["average_radius_std"],
    fmt="o",
    color="red",
    ecolor="lightcoral",
    elinewidth=2,
    capsize=3,
)
axs[2].set_title("Trial vs Average Radius")
axs[2].set_xlabel("Trial")
axs[2].set_ylabel("Average Radius (microns)")
axs[2].axhline(125, color="gray", ls="--", lw=1.5, label="Desired Radius (125 microns)")
axs[2].legend()

# label (a), (b), (c) for the three subplots
axs[0].text(
    -0.1, 1.05, "(a)", transform=axs[0].transAxes, fontsize=15, fontweight="bold"
)
axs[1].text(
    -0.1, 1.05, "(b)", transform=axs[1].transAxes, fontsize=15, fontweight="bold"
)
axs[2].text(
    -0.1, 1.05, "(c)", transform=axs[2].transAxes, fontsize=15, fontweight="bold"
)
# fig.suptitle('Trial Parameter Relationships', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig("trial_parameter_relationships.svg")
plt.show()


# %%
custom_weights = {
    "roundness": 0,
    "haz": 0,
    "radius_ablated": 0,
    "cracking": 1,
}
row1 = 118
row2 = 121
print(
    f"looking at trials {parameterSheet[row1][0]} and {parameterSheet[row2][0]} with custom weights:"
)
# compare row 121 with 125 with and without custom weights
print("\nWithout custom weights:")
print("trial 121:", objectiveScore(*parameterSheet[121][1:7]))
print("trial 125:", objectiveScore(*parameterSheet[125][1:7]))
print("\nWith custom weights:")
print("trial 121:", objectiveScore(*parameterSheet[121][1:7], weights=custom_weights))
print("trial 125:", objectiveScore(*parameterSheet[125][1:7], weights=custom_weights))

# %%
# %%
# %%
# %%
import numpy as np
import pandas
import matplotlib.pyplot as plt

# ── Load data ─────────────────────────────────────────────────────────────────
parameterFilepath = r"ImagesToTest/backupParameterMeasurement2025-04-29.xlsx"
parameterSheet = pandas.read_excel(
    parameterFilepath,
    sheet_name="Measurements",
).to_numpy()


def objectiveScore(
    HAZArea,
    cleanCutArea,
    perimeter,
    averageRadius,
    crackingPresent,
    totalTime,
    weights=None,
):
    if weights is None:
        weights = {"roundness": 0.4, "haz": 0.2, "radius_ablated": 0.2, "cracking": 0.2}
    try:
        if any(v != v for v in [HAZArea, cleanCutArea, perimeter, averageRadius]):
            return 0.0
        if float(totalTime) > 350 or float(perimeter) == 0 or float(HAZArea) == 0:
            return 0.0
    except (TypeError, ValueError):
        return 0.0
    desired_radius = 311.75
    return 1 - (
        weights["roundness"] * (1 - 4 * np.pi * (cleanCutArea / perimeter**2))
        + weights["haz"] * (HAZArea - cleanCutArea) / HAZArea
        + weights["radius_ablated"]
        * abs(desired_radius - averageRadius)
        / desired_radius
        + weights["cracking"] * crackingPresent
    )


# ── Group 4 replicates per trial ──────────────────────────────────────────────
trial_data = {}
for i in range(1, len(parameterSheet)):
    row = parameterSheet[i]
    try:
        t = int(float(row[0]))
        if np.isnan(float(row[0])):
            continue
    except (TypeError, ValueError):
        continue
    trial_data.setdefault(t, []).append(row[1:7])

baseline_weights = {
    "roundness": 0.4,
    "haz": 0.2,
    "radius_ablated": 0.2,
    "cracking": 0.2,
}
weight_names = ["roundness", "haz", "radius_ablated", "cracking"]
label_map = {
    "roundness": "Roundness",
    "haz": "HAZ",
    "radius_ablated": "Radius",
    "cracking": "Cracking",
}
colors = ["#2196F3", "#FF5722", "#4CAF50", "#9C27B0"]

trials = [
    {
        "trial": t,
        "rows": trial_data[t],
        "baseline_score": np.mean([objectiveScore(*r) for r in trial_data[t]]),
    }
    for t in sorted(trial_data)
]

baseline_scores = [td["baseline_score"] for td in trials]
baseline_mean = np.mean([s for s in baseline_scores if s > 0])
baseline_top = trials[int(np.argmax(baseline_scores))]["trial"]
print(f"Baseline mean: {baseline_mean:.4f}  |  Top trial: {baseline_top}")

# ── Panel B: OAT top-trial stability ─────────────────────────────────────────
sweep = np.linspace(0.01, 0.99, 60)
oat_top = {}
for focus in weight_names:
    others = [k for k in weight_names if k != focus]
    obs = sum(baseline_weights[k] for k in others)
    top_list = []
    i = 0
    for wf in sweep:
        remaining = 1.0 - wf
        w = {k: baseline_weights[k] / obs * remaining for k in others}
        w[focus] = wf
        # print first 5 weights for focus "roundness"
        if focus == "haz" and i < 5:
            print(f"Weight set {i+1} for focus '{focus}': {w}")
        i += 1
        scores = [
            np.mean([objectiveScore(*r, weights=w) for r in td["rows"]])
            for td in trials
        ]
        top_list.append(trials[int(np.argmax(scores))]["trial"])
    oat_top[focus] = top_list

# print the top trial when it is not the same as baseline top for focus "haz"
print("\nTop trials for 'HAZ' focus when different from baseline top:")
for i, t in enumerate(oat_top["roundness"]):
    if t != baseline_top:
        print(f"Weight {sweep[i]:.2f} -> Top trial: {t}")

# ── Panel K: per-trial robustness across Dirichlet simplex ───────────────────
rng = np.random.default_rng(42)
weight_samples = rng.dirichlet(np.ones(4), size=3000)

# print weight samples for first 5 samples
print("First 5 weight samples (roundness, haz, radius_ablated, cracking):")
for i in range(5):
    print(weight_samples[i])

trial_means, trial_stds = [], []
for td in trials:
    scores = [
        np.mean(
            [
                objectiveScore(*r, weights=dict(zip(weight_names, ws)))
                for r in td["rows"]
            ]
        )
        for ws in weight_samples
    ]
    trial_means.append(np.mean(scores))
    trial_stds.append(np.std(scores))

trial_means = np.array(trial_means)
trial_stds = np.array(trial_stds)
trial_nums = np.array([td["trial"] for td in trials])

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, (ax_b, ax_k) = plt.subplots(1, 2, figsize=(14, 5))
# fig.patch.set_facecolor("#F5F7FA")

# B: Top trial stability
for idx, (key, color) in enumerate(zip(weight_names, colors)):
    stable = [1 if t == baseline_top else 0 for t in oat_top[key]]
    y = [idx + 0.55 * s - 0.5 for s in stable]
    # trim for only when stable is 1
    y_stable = [y[i] for i in range(len(stable)) if stable[i] == 1]
    sweep_stable = [sweep[i] for i in range(len(stable)) if stable[i] == 1]
    ax_b.plot(
        sweep_stable,
        y_stable,
        color=color,
        lw=2.5,
    )  # label=label_map[key])
    # ax_b.axvline(baseline_weights[key], color=color, ls=":", alpha=0.5, lw=1.2,label=f"Baseline {label_map[key]}")
ax_b.axvline(
    0.2,
    color="blue",
    ls="--",
    lw=1.3,
    alpha=0.7,
    label="Baseline weight (HAZ, Radius, Cracking)",
)
ax_b.axvline(
    0.4, color="red", ls="--", lw=1.3, alpha=0.7, label="Baseline weight (Roundness)"
)
ax_b.set_facecolor("white")
ax_b.legend(fontsize=9, loc="upper right")
ax_b.set_yticks(range(len(weight_names)))
ax_b.set_yticklabels([label_map[k] for k in weight_names], fontsize=11)
ax_b.set_xlabel("Weight value  (others rescaled — sum always = 1)", fontsize=10)
ax_b.set_title(
    f"Top Trial Stability\n(line = same winner as baseline Trial {baseline_top})\nweights varied one at a time, others rescaled to sum to 1",
    fontsize=12,
    fontweight="bold",
)
# ax_b.set_xlim(0, 1)
ax_b.set_ylim(-0.6, len(weight_names))

# K: Per-trial robustness
mask = trial_means > 0.05
ax_k.errorbar(
    trial_nums[mask],
    trial_means[mask],
    yerr=trial_stds[mask],
    fmt="o",
    color="#FF5722",
    ecolor="#FFCCBC",
    elinewidth=2,
    capsize=3,
    markersize=5,
    alpha=0.9,
    label="Trial mean ± SD across 3000 random weight sets",
)
ax_k.scatter(
    trial_nums[mask],
    np.array(baseline_scores)[mask],
    color="green",
    marker="x",
    s=35,
    zorder=4,
    label="Baseline Score",
)
# ax_k.axhline(
#     baseline_mean,
#     color="blue",
#     ls="--",
#     lw=1.3,
#     alpha=0.7,
#     label=f"Baseline mean: {baseline_mean:.3f}",
# )
top_mask = trial_nums == baseline_top
ax_k.errorbar(
    trial_nums[top_mask],
    trial_means[top_mask],
    yerr=trial_stds[top_mask],
    fmt="*",
    color="gold",
    ecolor="#FFCCBC",
    elinewidth=2,
    capsize=4,
    markersize=14,
    markeredgecolor="black",
    zorder=5,
    label=f"Top trial ({baseline_top})",
)
# plot the trials with the base weights in green
ax_k.set_facecolor("white")
ax_k.set_xlabel("Trial number", fontsize=10)
ax_k.set_ylabel("Objective Score", fontsize=10)
ax_k.set_title(
    "Per-Trial Score Robustness to Weight Variation\n"
    "(error bars = SD across 3000 random weight sets, all summing to 1)",
    fontsize=12,
    fontweight="bold",
)
ax_k.legend(fontsize=9)
# add (a) and (b) labels to panels
ax_b.text(-0.1, 1.05, "(a)", transform=ax_b.transAxes, fontsize=12, fontweight="bold")
ax_k.text(-0.1, 1.05, "(b)", transform=ax_k.transAxes, fontsize=12, fontweight="bold")
fig.suptitle(
    "Objective Function Weight Sensitivity Analysis", fontsize=14, fontweight="bold"
)
plt.tight_layout()
plt.savefig(
    "sensitivity_analysis.svg",
    dpi=150,
    bbox_inches="tight",
    facecolor=fig.get_facecolor(),
)
print("Saved: sensitivity_analysis.png")
plt.show()

# %%
