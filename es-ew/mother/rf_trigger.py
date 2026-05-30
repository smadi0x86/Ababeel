import time
import logging
import pandas as pd
import os

logger = logging.getLogger("RF_Trigger")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")

try:
    import numpy as np
    from rtlsdr import RtlSdr
    SDR_AVAILABLE = True
except ImportError:
    logger.warning("rtlsdr or numpy not installed. Running in SIMULATION mode.")
    SDR_AVAILABLE = False

def monitor_rf_trigger(callback, freq=433.92e6, threshold=0.5, simulate=False):
    if simulate or not SDR_AVAILABLE:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'random-2ghz-4ghz-pdw-list.csv')
        if os.path.exists(csv_path):
            logger.info(f"SIMULATION mode: Loading PDWs from {csv_path}")
            df = pd.read_csv(csv_path, sep=';')
            chunk_size = 100
            try:
                for i in range(0, len(df), chunk_size):
                    chunk = df.iloc[i:i+chunk_size]
                    time.sleep(2.0)
                    logger.info(f"Mocking batch of {len(chunk)} PDWs...")
                    callback(chunk)
            except KeyboardInterrupt:
                pass
        else:
            logger.warning(f"SIMULATION mode: {csv_path} not found. Returning empty dataframe.")
            time.sleep(5.0)
            callback(pd.DataFrame(columns=['FREQ', 'START_TIME', 'POW']))
        return

    sdr = None
    try:
        sdr = RtlSdr()
        sdr.sample_rate = 2.048e6
        sdr.center_freq = freq
        sdr.gain = 'auto'
    except Exception as e:
        logger.error(f"Failed to initialize RTL-SDR hardware: {e}")
        logger.info("Falling back to SIMULATION mode.")
        return monitor_rf_trigger(callback, freq, threshold, simulate=True)

    logger.info(f"RF Trigger armed on {freq/1e6} MHz. Awaiting pulses > {threshold}...")
    
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'random-2ghz-4ghz-pdw-list.csv')
    pdw_df = pd.DataFrame(columns=['FREQ', 'START_TIME', 'POW'])
    if os.path.exists(csv_path):
        pdw_df = pd.read_csv(csv_path, sep=';')
        
    try:
        while True:
            samples = sdr.read_samples(256 * 1024)
            mag = np.abs(samples)
            if np.max(mag) > threshold:
                logger.info(f"Hardware RF Spike Detected! Max magnitude: {np.max(mag):.2f}")
                if not pdw_df.empty:
                    start_idx = np.random.randint(0, max(1, len(pdw_df) - 100))
                    chunk = pdw_df.iloc[start_idx:start_idx+100]
                    logger.info(f"Injecting High-Fidelity 3.2GHz SAM simulation chunk (100 PDWs)...")
                    callback(chunk)
                else:
                    logger.warning("No PDW CSV found. Returning empty dataframe.")
                    callback(pd.DataFrame(columns=['FREQ', 'START_TIME', 'POW']))
                time.sleep(2.0)
    except KeyboardInterrupt:
        logger.info("RF Trigger terminated via keyboard.")
    finally:
        if sdr:
            sdr.close()
