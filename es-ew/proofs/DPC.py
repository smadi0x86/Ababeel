import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform

def run_dpc(data_norm, dc_percentile=2.0):
    dist_matrix = squareform(pdist(data_norm))
    dc = np.percentile(dist_matrix, dc_percentile)
    rho = np.sum(np.exp(-(dist_matrix / dc)**2), axis=1)
    
    delta = np.zeros_like(rho)
    sorted_idx = np.argsort(-rho)
    delta[sorted_idx[0]] = np.max(dist_matrix)
    for i in range(1, len(data_norm)):
        idx = sorted_idx[i]
        higher_density_indices = sorted_idx[:i]
        delta[idx] = np.min(dist_matrix[idx, higher_density_indices])
    return rho, delta

# 1. LOAD NEW REALISTIC DATA
df = pd.read_csv('random-2ghz-4ghz-pdw-list.csv', sep=';')

# 2. FEATURE EXTRACTION (FREQ + TIME + POWER)
# Use POW instead of Amplitude to match your CSV headers
X_raw = df[['FREQ', 'START_TIME', 'POW']].values

# 3. ROBUST NORMALIZATION
std = np.std(X_raw, axis=0)
std[std == 0] = 1.0
X_norm = (X_raw - np.mean(X_raw, axis=0)) / std

# 4. EXECUTE
rho, delta = run_dpc(X_norm)
gamma = rho * delta
peaks = np.where(gamma > np.percentile(gamma, 99.7))[0]

# 5. VISUALIZE
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), facecolor='black')
ax1.set_facecolor('black')
ax1.scatter(rho, delta, c='#00CED1', s=15, alpha=0.3)
ax1.scatter(rho[peaks], delta[peaks], c='#FF0000', s=100, edgecolors='white', label='Emitter Centroids')
ax1.set_title("DPC DECISION GRAPH", color='white', weight='bold')

ax2.set_facecolor('black')
ax2.scatter(df['START_TIME'], df['FREQ']/1e6, c='#404040', s=5, alpha=0.3, label='Interleaved Stream')
ax2.scatter(df.iloc[peaks]['START_TIME'], df.iloc[peaks]['FREQ']/1e6, c='#FF0000', marker='X', s=200, label='Target Signal Lock')
ax2.set_title("PHASE 1: SIGNAL ISOLATION", color='white', weight='bold')
ax2.set_ylabel("Frequency (MHz)")

plt.tight_layout()
plt.show()

# 6. VERIFY OUTPUT
for i, idx in enumerate(peaks):
    print(f"Emitter {i+1} Lock: {df.iloc[idx]['FREQ']/1e6:.2f} MHz at {df.iloc[idx]['START_TIME']:.4f}s")
