from skopt import Optimizer
from skopt.space import Real, Integer
import numpy as np
import matplotlib.pyplot as plt
import pandas
from skopt.plots import (
    plot_evaluations,
    plot_objective,
    plot_convergence,
    plot_gaussian_process,
)

parameterSheet = pandas.read_excel(
    "ImagesToTest/2025-02-24/parametersVsQualityLocal2025-02-24.xlsx",
    sheet_name="Parameters",
).to_numpy()


initial_parameters = []
initial_quality_factors = []

for trialNumber in range(1, len(parameterSheet)):
    initial_parameters.append(list(parameterSheet[trialNumber, 1:6]))
    initial_quality_factors.append(parameterSheet[trialNumber, 6])
# initial_parameters = np.array(initial_parameters)
# initial_quality_factors = np.array(initial_quality_factors)
print(initial_parameters)
print(initial_quality_factors)
# Define the parameter space
space = [
    Real(1, 3, name="Power"),  # Pulse energy (J)
    Real(
        17, 21.5, name="FocalPosition"
    ),  # Position of slide (mm) with respect to bessel characterization
    Real(1, 150, name="scan_speed"),  # Software Scan speed (mm/s)
    Real(0.001, 0.01, name="HatchSpacing"),  # Spacing of hatch (m)
    Integer(0, 40, name="Repeats"),  # Number of times to repeat circle (unitless)
]


# Define some constraints
def outputConstraints(params):
    pulse_energy, focal_position, scan_speed, hatch_spacing, repeats = params
    # Test timelieness
    if (0.5 * 2 * np.pi) * repeats * 10 * 4 / (
        scan_speed * 0.25
    ) > 150:  # Example maximum time requirement
        return False  # Constraint violated
    return True  # Constraint satisfied


# Initialize the optimizer
optimizer = Optimizer(
    dimensions=space,
    random_state=0,
    acq_func="PI",
    acq_func_kwargs={"xi": 0.1},
)  # Set random_state to None for randomization of outputs, generate next suggested parameters with random_state=0,1,2

# Feed the initial data to the optimizer
for params, quality in zip(initial_parameters, initial_quality_factors):
    if quality == 0:
        quality = -00
    optimizer.tell(params, -quality)  # Negate quality factor since we are minimizing

# Perform iterative optimization

# Get the next suggested parameter set
requested_points = 5
suggested_params = optimizer.ask(n_points=requested_points, strategy="cl_min")
# Limit those that are outside of our time constraint
valid_suggestions = [p for p in suggested_params if outputConstraints(p)]
invalid_suggestions = [p for p in suggested_params if not outputConstraints(p)]

while len(invalid_suggestions) > 0:
    print("FEEDING INVALID SUGGESTIONS")
    for params in invalid_suggestions:
        optimizer.tell(params, 0)  # Quality factor 0 for invalid suggestions
    suggested_params = optimizer.ask(n_points=requested_points, strategy="cl_min")
    # Limit those that are outside of our time constraint
    # suggested_params = [p for p in suggested_params if outputConstraints(p)]
    valid_suggestions = [p for p in suggested_params if outputConstraints(p)]
    invalid_suggestions = [p for p in suggested_params if not outputConstraints(p)]

suggested_params = valid_suggestions

# Print the suggested parameters
"""
for i in range(len(suggested_params)):
    print(f"Suggested Parameters for Trial {len(initial_parameters) + i + 1}:")
    print(
        f"Pulse Energy: {suggested_params[i][0]:.7e} J Based off PP: {suggested_params[i][0]*20000/suggested_params[i][1]} W"
    )
    print(f"Pulse Picker: {suggested_params[i][1]}")
    print(f"Focal Position: {suggested_params[i][2]:.2f} mm")
    print(f"Scan Speed: {suggested_params[i][3]:.2f} mm/s")
    print(f"Hatch Distance: {suggested_params[i][4]:.3f} mm")
    print(f"Repeats: {suggested_params[i][5]:.2f}\n")
"""

tested_parameters = np.array(optimizer.Xi)
tested_quality_factors = np.array(optimizer.yi)
# print("\nAll Parameters Tested:")
# for params, quality in zip(optimizer.Xi, [-q for q in optimizer.yi]):
#    print(f"Parameters: {params}, Quality Factor: {quality:.3f}")
print("\nSuggested Next Parameters:")
for i in range(len(suggested_params)):
    print(
        f"Power: {suggested_params[i][0]*20000/suggested_params[i][1]}",
        suggested_params[i],
    )

# Plot quality factor vs iteration
plt.figure(figsize=(8, 6))
plt.plot(
    range(1, len(tested_quality_factors) + 1),
    tested_quality_factors,
    marker="o",
    label="Quality Factor",
)
plt.xlabel("Iteration")
plt.ylabel("Quality Factor")
plt.title("Optimization Progress")
plt.legend()
plt.show()


"""
# Visualizing optimization process: https://scikit-optimize.github.io/stable/auto_examples/plots/visualizing-results.html
plot_evaluations(optimizer.get_result())
plt.show()

plot_objective(optimizer.get_result())
plt.show()

plot_convergence(optimizer.get_result())
plt.show()
"""


def plot_acquisition_2D_slice(optimizer, space, dim_x, dim_y, fixed_params):
    """
    Visualize a 2D slice of the acquisition function.

    :param optimizer: Optimizer object
    :param space: Parameter space
    :param dim_x: Index of the first varying dimension
    :param dim_y: Index of the second varying dimension
    :param fixed_params: List of fixed parameter values
    """
    # Generate grid for the two selected dimensions
    x_range = np.linspace(space[dim_x].low, space[dim_x].high, 50)
    y_range = np.linspace(space[dim_y].low, space[dim_y].high, 50)
    X, Y = np.meshgrid(x_range, y_range)

    # Prepare parameter sets for prediction
    grid_params = [fixed_params.copy() for _ in range(len(X.ravel()))]
    for i, (x, y) in enumerate(zip(X.ravel(), Y.ravel())):
        grid_params[i][dim_x] = x
        grid_params[i][dim_y] = y

    # Predict acquisition function values
    grid_params = [fixed_params.copy() for _ in range(len(X.ravel()))]
    for i, (x, y) in enumerate(zip(X.ravel(), Y.ravel())):
        grid_params[i][dim_x] = x
        grid_params[i][dim_y] = y

    # Get mean and std predictions
    mean, std = optimizer.models[-1].predict(grid_params, return_std=True)

    # Debug: Check range of mean and std
    print(f"Mean Prediction Range: Min={np.min(mean)}, Max={np.max(mean)}")
    print(f"Std Prediction Range: Min={np.min(std)}, Max={np.max(std)}")

    Z = optimizer.models[-1].predict(grid_params).reshape(X.shape)
    print(Z)
    print("Min MAx of Z")
    print(np.min(Z))
    print(np.max(Z))

    # Plot the acquisition function
    plt.figure(figsize=(8, 6))
    plt.contourf(X, Y, Z, levels=50, cmap="viridis")
    # plt.colorbar(label="Acquisition Function Value")
    plt.xlabel(space[dim_x].name)
    plt.ylabel(space[dim_y].name)
    plt.title(
        f"2D Slice of Acquisition Function: {space[dim_x].name} vs {space[dim_y].name}"
    )
    plt.show()


def get_fixed_params(strategy="best"):
    """
    Determine fixed parameter values based on a given strategy.

    :param strategy: "best" for best-performing parameters, "average" for mean values
    :return: List of fixed parameter values
    """
    if strategy == "best":
        # Find the best parameters based on the highest quality factor
        best_index = np.argmax([-q for q in optimizer.yi])
        fixed_params = optimizer.Xi[best_index]
    elif strategy == "average":
        # Compute the average of all tested parameters
        fixed_params = np.mean(optimizer.Xi, axis=0)
    else:
        raise ValueError("Invalid strategy. Use 'best' or 'average'.")
    print(f"Fixed Parameters: {fixed_params}")
    return fixed_params


fixed_params = [0.0001, 2, 19, 75, 0.005, 10]
plot_acquisition_2D_slice(optimizer, space, 0, 3, get_fixed_params(strategy="average"))

best_index = np.argmax([-q for q in optimizer.yi])
best_params = optimizer.Xi[best_index]
best_quality = -optimizer.yi[best_index]

print("\nBest Predicted Parameters:")
print(f"  Parameters: {best_params}")
print(f"  Quality Factor: {best_quality:.3f}")
