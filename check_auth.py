# check_auth.py
from app.utils.auth import hash_password, verify_password

password_to_test = "admin123"
# Le hash exact que vous avez mis dans le SQL
sql_hash = "$argon2id$v=19$m=65536,t=3,p=4$7Y5Wp8W1S6lF6z1N2q9Q5w$O7N8/v5J8J8"

# 1. Test de vérification
is_valid = verify_password(password_to_test, sql_hash)
print(f"Match SQL hash: {is_valid}")

# 2. Test de génération
new_hash = hash_password(password_to_test)
print(f"New hash generated: {new_hash}")
print(f"Match new hash: {verify_password(password_to_test, new_hash)}")