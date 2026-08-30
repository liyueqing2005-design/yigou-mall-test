import os

API_URL = os.getenv("YIGOU_API_URL", "http://localhost:8080/api")
WEB_URL = os.getenv("YIGOU_WEB_URL", "http://localhost:5173")

BUYER = {"id": 1, "username": "buyer", "password": "123456"}
SELLER = {"id": 2, "username": "seller", "password": "123456"}
ADMIN = {"id": 3, "username": "admin", "password": "123456"}

CART_TEST_PRODUCT_ID = 5
