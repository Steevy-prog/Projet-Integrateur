import hashlib

# Input text
text = "mysecretpassword"

# Encode and hash it
hash_object = hashlib.sha256(text.encode())
hex_dig = hash_object.hexdigest()

print("SHA-256 Hash:", hex_dig)