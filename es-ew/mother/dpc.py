import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform

class DensityPeakCluster:
    def __init__(self, dc_percentile=2.0):
        self.dc_percentile = dc_percentile
    
    def _run_dpc(self, data_norm):
        dist_matrix = squareform(pdist(data_norm))
        # Handle case where matrix is 1 element or distance is 0 everywhere
        if np.all(dist_matrix == 0):
            return np.ones(len(data_norm)), np.zeros(len(data_norm))
            
        dc = np.percentile(dist_matrix, self.dc_percentile)
        if dc == 0:
            dc = 1e-6 # prevent division by zero
            
        rho = np.sum(np.exp(-(dist_matrix / dc)**2), axis=1)
        
        delta = np.zeros_like(rho)
        sorted_idx = np.argsort(-rho)
        delta[sorted_idx[0]] = np.max(dist_matrix)
        for i in range(1, len(data_norm)):
            idx = sorted_idx[i]
            higher_density_indices = sorted_idx[:i]
            delta[idx] = np.min(dist_matrix[idx, higher_density_indices])
        return rho, delta

    def cluster(self, pdw_df):
        """
        Takes a pandas DataFrame of PDWs containing ['FREQ', 'START_TIME', 'POW'].
        Returns the dominant frequency and its power, ignoring interleaved noise.
        """
        if pdw_df is None or pdw_df.empty:
            return 433.92e6, -50.0

        if len(pdw_df) < 3:
            strongest = pdw_df.iloc[pdw_df['POW'].argmax()]
            return strongest['FREQ'], strongest['POW']

        X_raw = pdw_df[['FREQ', 'START_TIME', 'POW']].values
        
        std = np.std(X_raw, axis=0)
        std[std == 0] = 1.0
        X_norm = (X_raw - np.mean(X_raw, axis=0)) / std
        
        rho, delta = self._run_dpc(X_norm)
        gamma = rho * delta
        
        percentile_val = np.percentile(gamma, 99.7)
        peaks = np.where(gamma > percentile_val)[0]
        
        if len(peaks) > 0:
            best_idx = peaks[np.argmax(gamma[peaks])]
            best_pdw = pdw_df.iloc[best_idx]
            return best_pdw['FREQ'], best_pdw['POW']
        
        strongest = pdw_df.iloc[pdw_df['POW'].argmax()]
        return strongest['FREQ'], strongest['POW']
