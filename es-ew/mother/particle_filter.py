import numpy as np
from scipy.stats import norm

class ParticleFilter:
    def __init__(self, num_particles=10000, bearing_noise_std_deg=2.5):
        self.num_particles = num_particles
        self.bearing_noise_std = np.radians(bearing_noise_std_deg)
        self.particles = None
        self.weights = np.ones(num_particles) / num_particles
        
    def _systematic_resample(self, weights):
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

    def _angular_diff_vectorized(self, a, b):
        return (a - b + np.pi) % (2 * np.pi) - np.pi

    def initialize_particles(self, uav_lat, uav_lon):
        # Initialize particles in a +/- 0.1 degree box (~11km)
        self.particles = np.column_stack((
            np.random.uniform(uav_lat - 0.1, uav_lat + 0.1, self.num_particles),
            np.random.uniform(uav_lon - 0.1, uav_lon + 0.1, self.num_particles)
        ))
        self.weights = np.ones(self.num_particles) / self.num_particles

    def update(self, uav_lat, uav_lon, uav_heading, measurement_bearing):
        if self.particles is None:
            self.initialize_particles(uav_lat, uav_lon)
            
        uav_pos = np.array([uav_lat, uav_lon])
        meas_bearing_rad = np.radians(measurement_bearing)
        
        expected_bearings = np.arctan2(
            self.particles[:, 1] - uav_pos[1], 
            self.particles[:, 0] - uav_pos[0]
        )
        
        errors = self._angular_diff_vectorized(meas_bearing_rad, expected_bearings)
        
        self.weights *= norm.pdf(errors, 0, self.bearing_noise_std)
        self.weights += 1.e-300
        self.weights /= np.sum(self.weights)
        
        ess = 1.0 / np.sum(np.square(self.weights))
        if ess < self.num_particles / 2.0:
            indices = self._systematic_resample(self.weights)
            self.particles = self.particles[indices]
            self.weights.fill(1.0 / self.num_particles)
            self.particles += np.random.normal(0, 0.0001, size=self.particles.shape)
            
        return self.particles
