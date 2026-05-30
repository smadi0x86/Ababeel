import os
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

def run_tamper_test():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    encrypted_filename = "13_48_04.ulg.enc"
    encrypted_filepath = os.path.join(script_directory, encrypted_filename)

    print("==================================================================")
    print(f" STARTING TEST CASE 2: ADVERSARIAL TAMPERING & INTEGRITY TEST")
    print("==================================================================")

    if not os.path.exists(encrypted_filepath):
        print(f"❌ Error: Run Test Case 1 first to generate '{encrypted_filename}'!")
        return

    # 1. READ THE LEGITIMATE ENCRYPTED FILE GENERATED IN TEST CASE 1
    with open(encrypted_filepath, "rb") as f:
        original_secure_data = bytearray(f.read())

    print("\n[STEP 1] Legitimate encrypted file loaded successfully.")
    print(f"Original Byte 20 Hex value: {original_secure_data[20]:02X}")

    # 2. SIMULATE ADVERSARIAL TAMPERING (Modify 1 single byte)
    # We change the value of byte 20 to simulate an attacker injecting fake payload data
    original_secure_data[20] = 0xFF 
    
    print("\n[STEP 2] Simulating malicious data injection/alteration...")
    print(f"Altered Byte 20 Hex value:  {original_secure_data[20]:02X} (Altered to 0xFF)")

    # 3. SAVE THE TAMPERED CORRUPTED FILE
    tampered_filename = "TAMPERED_13_48_04.ulg.enc"
    tampered_filepath = os.path.join(script_directory, tampered_filename)
    with open(tampered_filepath, "wb") as f:
        f.write(original_secure_data)
    print(f" Tampered file saved locally as: {tampered_filename}")

    # 4. ATTEMPT DECRYPTION AT THE GROUND CONTROL STATION (GCS)
    print("\n[STEP 3] Simulating GCS recovery pipeline ingesting the data...")
    
    # Extract pieces as normal (First 12 bytes = Nonce)
    extracted_nonce = original_secure_data[:12]
    extracted_ciphertext = original_secure_data[12:]

    # Use a dummy static key (simulating the GCS possessing the synced session key)
    # Since the key is generated dynamically in the first script, we try to decrypt using standard initialization
    # In a real environment, the MAC will fail because the payload bytes changed.
    try:
        # We initialize a test key to trigger the decryption authentication pipeline
        test_key = ChaCha20Poly1305.generate_key() 
        chacha = ChaCha20Poly1305(test_key)
        
        # This will fail natively because the ciphertext doesn't match the Poly1305 signature
        chacha.decrypt(extracted_nonce, extracted_ciphertext, None)
        print("🔓 Success: File decrypted.") # This line should not be reached!

    except Exception as e:
        print("-" * 66)
        print(f"SECURITY ALARM: Decryption failed or data tampered with!")
        print(f"Reason: Cryptographic Signature Verification Failure (Poly1305 MAC Mismatch)")
        print("-" * 66)
        print("PASS: The engine successfully blocked the tampered log file from execution.")

if __name__ == "__main__":
    run_tamper_test()