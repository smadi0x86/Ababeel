import os
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

def read_hex_preview(file_path, bytes_to_read=48):
    """
    Reads the first few bytes of a file and converts them to a readable Hex/ASCII preview.
    This demonstrates the structural difference before and after encryption.
    """
    if not os.path.exists(file_path):
        return "File not found."
    with open(file_path, "rb") as f:
        data = f.read(bytes_to_read)
    
    # Format as a clean Hexadecimal string layout
    hex_string = " ".join(f"{b:02X}" for b in data)
    # Format as readable ASCII text characters (replacing unprintable bytes with dots)
    ascii_string = "".join(chr(b) if 32 <= b <= 126 else "." for b in data)
    
    return f"HEX:   {hex_string}\nASCII: {ascii_string}"

def run_demonstration(input_filepath):
    # Extract just the filename for cleaner display prints
    filename = os.path.basename(input_filepath)
    
    print("==================================================================")
    print(f"STARTING CHACHA20 SECURE BLACK BOX DEMONSTRATION FOR: {filename}")
    print("==================================================================")
    
    if not os.path.exists(input_filepath):
        print(f"Error: Cannot find the file at:\n   {input_filepath}")
        print("\nFix: Make sure your .ulg file is in the exact same folder as this script!")
        return

    # 1. SHOW THE NORMAL RAW DATA BEFORE ENCRYPTION
    print("\n[STEP 1] Inspecting normal PX4 Log data before encryption:")
    print("-" * 66)
    print(read_hex_preview(input_filepath))
    print("-" * 66)
    print("Notice the file structure starts with distinct PX4 ULog magic headers (ULog).")

    # 2. GENERATE CRYPTOGRAPHIC KEY & UNIQUE NONCE
    # In our project design, this key is generated via the ALE handshake and stays strictly in volatile RAM.
    chacha_key = ChaCha20Poly1305.generate_key()
    nonce = os.urandom(12) # 12-byte unique initialization vector required by ChaCha20
    
    # 3. RUN CHACHA20 ENCRYPTION (Simulating Pre-SD Card Storage)
    with open(input_filepath, "rb") as f:
        raw_flight_data = f.read()
        
    chacha = ChaCha20Poly1305(chacha_key)
    # Encrypt the binary payload
    encrypted_payload = chacha.encrypt(nonce, raw_flight_data, None)
    
    # Define output path for the encrypted file in the same directory
    encrypted_filepath = input_filepath + ".enc"
    
    # Save the encrypted file (Prepending the nonce so we can parse it later)
    with open(encrypted_filepath, "wb") as f:
        f.write(nonce + encrypted_payload)
        
    print(f"\n [STEP 2] Flight details successfully encrypted using ChaCha20-Poly1305.")
    print(f" Secure file saved as: {os.path.basename(encrypted_filepath)}")

    # 4. SHOWING THE DATA AFTER ENCRYPTION
    print("\n[STEP 3] Inspecting the secured Black Box file data:")
    print("-" * 66)
    print(read_hex_preview(encrypted_filepath))
    print("-" * 66)
    print(" Notice that all recognizable patterns and headers are gone. It is now pure high-entropy chaos.")

    # 5. DECRYPTION (Simulating Ground Control Station Recovery)
    print("\n[STEP 4] Simulating data recovery at Ground Control Station...")
    
    with open(encrypted_filepath, "rb") as f:
        stored_data = f.read()
        
    # Extract the pieces (First 12 bytes = Nonce, everything after = Ciphertext)
    extracted_nonce = stored_data[:12]
    extracted_ciphertext = stored_data[12:]
    
    # Define output path for the decrypted recovery file
    decrypted_filepath = os.path.join(os.path.dirname(input_filepath), "RECOVERED_" + filename)
    
    try:
        # Decrypting and validating the Poly1305 authentication tag simultaneously
        decrypted_data = chacha.decrypt(extracted_nonce, extracted_ciphertext, None)
        
        with open(decrypted_filepath, "wb") as f:
            f.write(decrypted_data)
            
        print(f"[STEP 5] Authentication verified! File decrypted successfully.")
        print(f"Recovered log saved as: {os.path.basename(decrypted_filepath)}")
        
        print("\n[STEP 6] Inspecting recovered data verification:")
        print("-" * 66)
        print(read_hex_preview(decrypted_filepath))
        print("-" * 66)
        print("Success! The headers match the original flight file exactly.")
        
    except Exception as e:
        print(f"Security Alarm: Decryption failed or data tampered with. {e}")

if __name__ == "__main__":
    # ─── BULLETPROOF FILE PATH RESOLUTION ─────────────────────────────────────
    # This automatically detects the exact folder where this script is saved in the computer.
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    #  Choose the exact file name for encryption
    chosen_file = "13_48_04.ulg"
    
    # Merges the directory path and file name into a fully valid absolute path
    absolute_target_path = os.path.join(script_directory, chosen_file)
    
    # Execute the pipeline
    run_demonstration(absolute_target_path)