from skopt import Optimizer
from skopt.space import Real, Integer
import numpy as np
import matplotlib.pyplot as plt
import pandas
from skopt.plots import plot_evaluations, plot_objective, plot_convergence

parameterSheet = pandas.read_excel(
    "ImagesToTest/2024-12-10/parametersVsQualityLocal.xlsx", sheet_name="Parameters"
).to_numpy()


initial_parameters = []
initial_quality_factors = []

for trialNumber in range(1, len(parameterSheet)):
    initial_parameters.append(list(parameterSheet[trialNumber, 2:8]))
    initial_quality_factors.append(parameterSheet[trialNumber, 8])
# initial_parameters = np.array(initial_parameters)
# initial_quality_factors = np.array(initial_quality_factors)

# Define the parameter space
space = [
    Real(0.00006, 0.000151, name="pulse_energy"),  # Pulse energy (J)
    Integer(
        1, 30, name="PulsePicker"
    ),  # Pulse Picker (Laser is 20KhZ rep rate divided by pulse picker)
    Real(
        17, 21.5, name="FocalPosition"
    ),  # Position of slide (mm) with respect to bessel characterization
    Real(1, 100, name="scan_speed"),  # Scan speed (mm/s)
    Real(0.001, 0.01, name="HatchSpacing"),  # Spacing of hatch (m)
    Integer(0, 20, name="Repeats"),  # Number of times to repeat circle (unitless)
]

# Initial data (4 initial parameter sets and their corresponding quality factors)

print(initial_quality_factors)
# print(initial_quality_factors2)

# Initialize the optimizer
optimizer = Optimizer(
    dimensions=space, random_state=2
)  # Set random_state to None for randomization of outputs, generate next suggested parameters with random_state=0,1,2

# Feed the initial data to the optimizer
for params, quality in zip(initial_parameters, initial_quality_factors):
    optimizer.tell(params, -quality)  # Negate quality factor since we are minimizing

# Perform iterative optimization

# Get the next suggested parameter set
suggested_params = optimizer.ask(n_points=5, strategy="cl_mean")

# Print the suggested parameters
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


tested_parameters = np.array(optimizer.Xi)
tested_quality_factors = np.array(optimizer.yi)
print("\nAll Parameters Tested:")
for params, quality in zip(optimizer.Xi, [-q for q in optimizer.yi]):
    print(f"Parameters: {params}, Quality Factor: {quality:.3f}")
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

# Visualizing optimization process: https://scikit-optimize.github.io/stable/auto_examples/plots/visualizing-results.html
plot_evaluations(optimizer.get_result())
plt.show()

plot_objective(optimizer.get_result())
plt.show()

plot_convergence(optimizer.get_result())
plt.show()

best_index = np.argmax([-q for q in optimizer.yi])
best_params = optimizer.Xi[best_index]
best_quality = -optimizer.yi[best_index]

print("\nBest Predicted Parameters:")
print(f"  Parameters: {best_params}")
print(f"  Quality Factor: {best_quality:.3f}")


# Get the next suggested parameter sets
n_points = 50
suggested_params = optimizer.ask(n_points=n_points, strategy="cl_mean")

# Predict the objective values for the suggested parameters
predicted_objectives = optimizer.models[-1].predict(suggested_params)

# Find the best-predicted parameters
best_predicted_index = np.argmin(predicted_objectives)
best_predicted_params = suggested_params[best_predicted_index]
best_predicted_quality = -predicted_objectives[
    best_predicted_index
]  # Negate for quality factor

# Print the best-predicted parameters
print("\nBest Predicted Parameters (Not Yet Tested):")
print(f"  Pulse Energy: {best_predicted_params[0]:.7e} J")
print(f"  Pulse Picker: {best_predicted_params[1]}")
print(f"  Focal Position: {best_predicted_params[2]:.2f} mm")
print(f"  Scan Speed: {best_predicted_params[3]:.2f} mm/s")
print(f"  Hatch Distance: {best_predicted_params[4]:.3f} mm")
print(f"  Repeats: {best_predicted_params[5]}")
print(f"  Predicted Quality Factor: {best_predicted_quality:.3f}")
