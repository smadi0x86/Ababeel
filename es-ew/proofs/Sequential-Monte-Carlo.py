import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

def systematic_resample(weights):
    N = len(weights)
    positions = (np.random.random() + np.arange(N)) / N
    indices = np.zeros(N, dtype=int)
    cumulative_sum = np.cumsum(weights)
    i, j = 0, 0
    while i < N:
        if positions[i] < cumulative_sum[j]:
            indices[i] = j
            i += 1
        else:
            j += 1
    return indices

def angular_diff_vectorized(a, b):
    return (a - b + np.pi) % (2 * np.pi) - np.pi

target_pos = np.array([7000.0, 8000.0])
uav_path = np.array([[x, 2000.0] for x in np.linspace(0, 8000, 15)])
bearing_noise_std = np.radians(2.5) 
N_PARTICLES = 10000

particles = np.random.uniform(low=[0, 0], high=[10000, 10000], size=(N_PARTICLES, 2))
weights = np.ones(N_PARTICLES) / N_PARTICLES

fig, ax = plt.subplots(figsize=(12, 8), facecolor='black')
ax.set_facecolor('black')
plt.style.use('dark_background')

ax.grid(color='#1A1A1A', linestyle='-', linewidth=1.0, zorder=0)

for spine in ax.spines.values():
    spine.set_color('#FFFFFF')
ax.tick_params(axis='both', colors='#FFFFFF', labelsize=10)

for i, uav_pos in enumerate(uav_path):
    true_bearing = np.arctan2(target_pos[1] - uav_pos[1], target_pos[0] - uav_pos[0])
    measured_bearing = true_bearing + np.random.normal(0, bearing_noise_std)
    
    expected_bearings = np.arctan2(particles[:, 1] - uav_pos[1], particles[:, 0] - uav_pos[0])
    errors = angular_diff_vectorized(measured_bearing, expected_bearings)
    
    weights *= norm.pdf(errors, 0, bearing_noise_std)
    weights += 1.e-300
    weights /= np.sum(weights)
    
    ess = 1.0 / np.sum(np.square(weights))
    
    if ess < N_PARTICLES / 2.0:
        indices = systematic_resample(weights)
        particles = particles[indices]
        weights.fill(1.0 / N_PARTICLES)
        particles += np.random.normal(0, 60, size=particles.shape)

    if i % 3 == 0 or i == len(uav_path) - 1:
        ray_end = uav_pos + 15000 * np.array([np.cos(measured_bearing), np.sin(measured_bearing)])
        ax.plot([uav_pos[0], ray_end[0]], [uav_pos[1], ray_end[1]], color='#333333', linestyle='--', linewidth=1.0, zorder=1)

estimate = np.average(particles, weights=weights, axis=0)

ax.scatter(particles[:, 0], particles[:, 1], c='#00CED1', s=2, alpha=0.15, label='SMC Particle Density', zorder=2)
ax.plot(uav_path[:, 0], uav_path[:, 1], c='#FFFFFF', marker='^', markersize=7, linestyle='-', linewidth=1, label='UAV Intercept Baseline', zorder=3)
ax.scatter(estimate[0], estimate[1], c='#FFFF00', marker='+', s=150, linewidths=2, label='Converged Fix', zorder=4)
ax.scatter(target_pos[0], target_pos[1], facecolors='none', edgecolors='#FF0000', marker='s', s=150, linewidths=2, label='True Emitter Location', zorder=5)

ax.set_title("BEARINGS-ONLY KINEMATIC TARGETING", fontsize=14, color='#FFFFFF', weight='bold', pad=15)
ax.set_xlabel("EASTING (Meters)", color='#FFFFFF', fontsize=11)
ax.set_ylabel("NORTHING (Meters)", color='#FFFFFF', fontsize=11)
ax.set_xlim(0, 10000)
ax.set_ylim(0, 10000)

legend = ax.legend(loc='upper left', facecolor='black', edgecolor='#FFFFFF', framealpha=0.8)
for text in legend.get_texts():
    text.set_color('#FFFFFF')
    text.set_fontsize(10)

plt.tight_layout()
plt.show()
