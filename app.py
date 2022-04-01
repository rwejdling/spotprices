# Fetches data from https://www.energidataservice.dk/tso-electricity/elspotprices
# API documentation http://docs.ckan.org/en/latest/api/index.html#making-an-api-request

import time, json
import requests
from os import getenv, pipe
from datetime import datetime
from dateutil.parser import parse
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUXDB_TOKEN = getenv('INFLUXDB_TOKEN', None)
INFLUXDB_ORG = getenv('INFLUXDB_ORG', None)
INFLUXDB_BUCKET = getenv('INFLUXDB_BUCKET', 'default')
INFLUXDB_URL = getenv('INFLUXDB_URL', 'http://localhost:8086')

TAGS = ['name', 'modelid', 'type', 'uniqueid']
FIELDS = ['battery',
          'lastupdated',
          'temperature',
          'humidity',
          'pressure',
          'sunrise',
          'sunset']

API_URL = "https://api.energidataservice.dk"

def get_spotprices(limit=48):
  """
  Gives the spot prices 
  """
  try:
    header = {
      "Content-Type": "application/json;charset=utf-8"
    }
    
    url = f'{API_URL}/datastore_search?' \
          f'resource_id=elspotprices&' \
          f'limit={limit}&' \
          f'filters={{"PriceArea":"DK2"}}&' \
          f'sort=HourUTC desc'
    
    print(f"URL: {url}")

    return requests.get(url, headers=header).json()

  except Exception as ex:
      raise Exception(str(ex))

if __name__ == '__main__':
  '''
      For running locally
  '''
  spotprices = get_spotprices(48)
  # print(json.dumps(spotprices, indent=2))

  print("--------- Start CSV output ---------")
  print("HourDK;SpotPriceKwh")
  
  for record in spotprices['result']['records']:
    kwh_price_in_DKK = float(record['SpotPriceEUR']) * 7.45 / 1000
    print(f"{record['HourDK']};{kwh_price_in_DKK}")

  print("--------- End of CSV output ---------")