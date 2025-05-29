from werkzeug.security import generate_password_hash

# List of users
users = [
    {"username": "admin", "password": "admin123", "role": "admin"},
    {"username": "teacher1", "password": "teach123", "role": "teacher"},
    {"username": "teacher2", "password": "teach456", "role": "teacher"}
]

# Generate SQL statements with hashed passwords
for user in users:
    hashed = generate_password_hash(user["password"])
    print(f"INSERT INTO users (username, password_hash, role) VALUES ('{user['username']}', '{hashed}', '{user['role']}');")