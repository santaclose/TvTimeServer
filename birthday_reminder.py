import os
import json
import datetime

import moreos

JSON_FILE = "birthdays.json"

birthdays = dict()
if os.path.isfile(JSON_FILE):
	with open(JSON_FILE, 'r') as file:
		jsonObject = json.loads(file.read())
		for k in jsonObject.keys():
			day, month = k.split('/')
			birthdays[(int(day), int(month))] = jsonObject[k]

def remind():
	nowdate = datetime.datetime.now()
	tomorrowdate = nowdate + datetime.timedelta(days=1)
	if (nowdate.day, nowdate.month) in birthdays:
		message = f"Hoy cumple {birthdays[(nowdate.day, nowdate.month)]}."
		moreos.show_notification("Cumples", message)
	if (tomorrowdate.day, tomorrowdate.month) in birthdays:
		message = f"Manana cumple {birthdays[(tomorrowdate.day, tomorrowdate.month)]}\n"
		moreos.show_notification("Cumples", message)

if __name__ == "__main__":
	remind()
