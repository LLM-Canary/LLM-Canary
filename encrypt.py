from cryptography.fernet import Fernet

encryption_key = ".encryption_key.key"

# public
def generate_key():
    '''
    Generate a new encryption key and save it securely.
    '''
    key = Fernet.generate_key()
    with open(encryption_key, "wb") as key_file:
        key_file.write(key)

# public
def load_key():
    '''
    Load the encryption key from a file
    '''
    with open(encryption_key, "rb") as key_file:
        return key_file.read()

# public
def encrypt_file(key):
    '''
    Encrypt a file
    '''
    fernet = Fernet(key)
    with open('.env', "rb") as file:
        file_data = file.read()
    encrypted_data = fernet.encrypt(file_data)
    with open('.env' + ".enc", "wb") as encrypted_file:
        encrypted_file.write(encrypted_data)

# public
def decrypt_file(key):
    '''
    Decrypt a file
    '''
    fernet = Fernet(key)
    with open('.env.enc', "rb") as encrypted_file:
        encrypted_data = encrypted_file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    with open('.env.enc'[:-4], "wb") as decrypted_file:
        decrypted_file.write(decrypted_data)