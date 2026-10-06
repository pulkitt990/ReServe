import requests

print("Training...")
res = requests.post("http://localhost:8000/api/v1/forecasting/train/1")
print(res.json())

print("Predicting...")
res = requests.post("http://localhost:8000/api/v1/forecasting/predict/1?days=2")
print(res.json())
