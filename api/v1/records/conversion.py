import base64

# Original phone number
phone_number = "+919392996404"

# Step 1: Convert the string to bytes using UTF-8 encoding
bytes_phone = phone_number.encode('utf-8')

# Step 2: Encode the bytes into base64 bytes
b64_bytes = base64.b64encode(bytes_phone)

# Step 3: Convert base64 bytes to a standard string
b64_phone = b64_bytes.decode('utf-8')

print("Original Phone Number:", phone_number)
print("Base64 Encoded Phone Number:", b64_phone)
