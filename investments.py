import os
import json
import requests
import datetime

lastQueryTime = None

JSON_FILE_NAME = "investments.json"

def get_investments_object():
	if not os.path.exists(JSON_FILE_NAME):
		return None
	with open(JSON_FILE_NAME, 'r') as file:
		return json.loads(file.read())

def query():
	global lastQueryTime

	obj = get_investments_object()
	if obj is None:
		return

	currentTime = datetime.datetime.now()
	if lastQueryTime is not None and (currentTime - lastQueryTime) < datetime.timedelta(minutes=10):
		return
	lastQueryTime = currentTime
	currencySet = set()
	for x in obj:
		currencySet.add(x['currency'])
	coinRequestUrl = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(currencySet)}&vs_currencies=usd"
	coinRequestResponse = requests.get(coinRequestUrl).json()
	print("----PRICES-----")
	for k in coinRequestResponse.keys():
		print(f"{k}: {coinRequestResponse[k]['usd']:.5f} USD")
	print("----INVESTMENTS----")
	totalGains = 0
	for investment in obj:
		convertedValue = investment['valueUSD'] / investment['price']
		currentPrice = coinRequestResponse[investment['currency']]['usd']
		currentValueUSD = currentPrice * convertedValue
		currentGain = currentValueUSD - investment['valueUSD']
		totalGains += currentGain
		print(f"{investment['currency']}: {investment['valueUSD']:.2f} -> {currentValueUSD:.2f}  ({currentGain:.2f}) USD   -  bought at {investment['price']:.3f}")
	print(f"--------\nTOTAL GAINS: {totalGains:.2f} USD")

if __name__ == "__main__":
	query()
