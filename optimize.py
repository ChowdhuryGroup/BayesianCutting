from skopt import Optimizer
from skopt.space import Real, Integer
import numpy as np

# Define the parameter space
space = [
    Real(0.1, 2.0, name='pulse_energy'),  # Pulse energy (J)
    Integer(10, 1000, name='rep_rate'),   # Repetition rate (Hz)
    Real(1.0, 20.0, name='scan_speed')    # Scan speed (mm/s)
]

# Initial data (4 initial parameter sets and their corresponding quality factors)
initial_parameters = [
    [0.5, 200, 5.0],  # Parameter 1
    [1.0, 500, 10.0],  # Parameter 2
    [1.5, 750, 15.0],  # Parameter 3
    [1.2, 600, 8.0]    # Parameter 4
]
initial_quality_factors = [0.6, 0.75, 0.82, 0.65]  # Corresponding quality factors

# Initialize the optimizer
optimizer = Optimizer(dimensions=space, random_state=0)

# Feed the initial data to the optimizer
for params, quality in zip(initial_parameters, initial_quality_factors):
    optimizer.tell(params, -quality)  # Negate quality factor since we are minimizing

# Perform iterative optimization
n_experiments = 1  # Define how many additional experiments you want to run

for i in range(n_experiments):
    # Get the next suggested parameter set
    suggested_params = optimizer.ask()
    
    # Print the suggested parameters
    print(f"Suggested Parameters for Trial {len(initial_parameters) + i + 1}:")
    print(f"Pulse Energy: {suggested_params[0]:.3f}")
    print(f"Repetition Rate: {suggested_params[1]} Hz")
    print(f"Scan Speed: {suggested_params[2]:.2f} mm/s")
    
    # Simulate running the experiment or input real result
    # Replace this with actual experimental feedback
    pulse_energy, rep_rate, scan_speed = suggested_params
    simulated_quality = -(pulse_energy - 1.2)**2 - (rep_rate - 600)**2 / 50000 - (scan_speed - 10)**2 / 4  # Example simulation
    
    print(f"Measured Hole Quality Factor: {simulated_quality:.3f}")
    
    # Update the optimizer with the new result
    optimizer.tell(suggested_params, -simulated_quality)  # Negate for minimization

print("\nAll Parameters Tested:")
for params, quality in zip(initial_parameters + optimizer.Xi, initial_quality_factors + [-q for q in optimizer.yi]):
    print(f"Parameters: {params}, Quality Factor: {quality:.3f}")