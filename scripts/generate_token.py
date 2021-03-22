import jwt

# Generate token
token = jwt.encode({"userId": "admin"}, 'secret', algorithm='HS256')
print(token)