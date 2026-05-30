import pandas as pd
import numpy as np

n_pulses = 1000
# Professional headers matched to your ver.py output
cols = ['WAVE_STATE', 'START_TIME', 'MARKER', 'PULSE_WIDTH', 'WAVE_WSEG', 'OUTP_STATE', 'FREQ', 'POW', 'PHASE']

# --- EMITTER 1: AGILE SAM RADAR (The Target) ---
# Hopping between 3.2 GHz and 3.4 GHz
sam_n = 400
sam_data = {
    'WAVE_STATE': 1,
    'START_TIME': np.linspace(0.1, 0.9, sam_n),
    'MARKER': 1,
    'PULSE_WIDTH': np.random.normal(2e-6, 0.1e-6, sam_n),
    'WAVE_WSEG': 1,
    'OUTP_STATE': 1,
    'FREQ': np.random.uniform(3.2e9, 3.4e9, sam_n), # 3.2-3.4 GHz
    'POW': np.random.normal(-25, 2, sam_n),         # Strong signal
    'PHASE': np.random.uniform(0, 360, sam_n)
}

# --- BACKGROUND NOISE: INTERLEAVED CHAOS ---
noise_n = 600
noise_data = {
    'WAVE_STATE': 1,
    'START_TIME': np.random.uniform(0, 1, noise_n),
    'MARKER': 0,
    'PULSE_WIDTH': np.random.uniform(0.5e-6, 10e-6, noise_n),
    'WAVE_WSEG': 1,
    'OUTP_STATE': 1,
    'FREQ': np.random.uniform(2.0e9, 4.0e9, noise_n), # Full 2-4 GHz spread
    'POW': np.random.uniform(-70, -40, noise_n),      # Weak noise
    'PHASE': np.random.uniform(0, 360, noise_n)
}

df_sam = pd.DataFrame(sam_data)
df_noise = pd.DataFrame(noise_data)
df_final = pd.concat([df_sam, df_noise]).sample(frac=1).reset_index(drop=True)

df_final.to_csv('random-2ghz-4ghz-pdw-list.csv', index=False, sep=';')
print("Successfully generated 1000 realistic PDWs in 'random-2ghz-4ghz-pdw-list.csv'")
