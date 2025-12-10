from argon2 import PasswordHasher

ph = PasswordHasher()

password = "password123"
hashed = ph.hash(password)

print(f"Password: {password}")
print(f"Hashed: {hashed}")

# Test verify
try:
    ph.verify(hashed, password)
    print("✅ Verification: SUCCESS")
except:
    print("❌ Verification: FAILED")
