import requests
import json
import sys
from datetime import datetime, timedelta


def quit(str, code):
    print(str)
    sys.exit(code)


def load_config():
    try:
        with open("config.json", "r") as F:
            return json.load(F)
    except Exception as ex:
        quit("Error loading configuration file (config.json): " + str(ex))


def toISO8601(dt):
    return dt.isoformat()[:19] + "Z"


print("Download Octopus Energy Meter Readings")
cfg = load_config()

startTime = datetime.utcnow() - timedelta(365)
# print(toISO8601(startTime))

res = requests.get("%s/v1/electricity-meter-points/%s/meters/%s/consumption/?page_size=25000&period_from=%s" % (cfg["url"], cfg["mpan"], cfg["serial"], startTime), auth=(cfg["apikey"], ""))
if res.status_code != 200:
    quit("Error requesting data: " + res.status_code)

data = res.json()
# print(json.dumps(data, indent=3))

with open("data.csv", "w") as F:
    F.write("Start\tEnd\tConsumption\n")
    for rec in data["results"]:
        F.write("\"%s\"\t\"%s\"\t%s\n" % (
            rec["interval_start"],
            rec["interval_end"],
            rec["consumption"]
        ))
