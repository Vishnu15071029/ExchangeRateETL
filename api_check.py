import requests

url = "https://api.frankfurter.dev/v2/rates"
params = {
    "base": "usd",
    "quotes": "inr,eur,gbp",
}

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()

data = response.json()
print(data)