import json
import requests
import datetime

lastQueryTime = None

def get_investments_object():
	with open("investments.json", 'r') as file:
		return json.loads(file.read())

def query():
	global lastQueryTime
	currentTime = datetime.datetime.now()
	if lastQueryTime is not None and (currentTime - lastQueryTime) < datetime.timedelta(minutes=10):
		return
	lastQueryTime = currentTime
	obj = get_investments_object()
	url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,nano,cardano,dogecoin&vs_currencies=usd"
	data = requests.get(url).json()
	print("----PRICES-----")
	for k in data.keys():
		print(f"{k}: {data[k]['usd']:.5f} USD")
	print("----INVESTMENTS----")
	totalGains = 0
	for investment in obj:
		convertedValue = investment['valueUSD'] / investment['price']
		currentPrice = data[investment['currency']]['usd']
		currentValueUSD = currentPrice * convertedValue
		currentGain = currentValueUSD - investment['valueUSD']
		totalGains += currentGain
		print(f"{investment['currency']}: {investment['valueUSD']:.2f} -> {currentValueUSD:.2f}  ({currentGain:.2f}) USD   -  bought at {investment['price']:.3f}")
	print(f"--------\nTOTAL GAINS: {totalGains:.2f} USD")

if __name__ == "__main__":
	query()
