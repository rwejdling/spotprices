# Fetches data from https://www.energidataservice.dk/tso-electricity/elspotprices
# API documentation http://docs.ckan.org/en/latest/api/index.html#making-an-api-request

from pickle import FALSE
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

SPOTPRICE_API_URL = "https://api.energidataservice.dk/datastore_search?"

# DK1 for DK_WEST and DK2 for DK_EAST
SPOTPRICE_AREA = getenv('SPOTPRICE_AREA', 'DK2') 

# Number of records to request (desc by HourUTC)
SPOTPRICE_REQUEST_LIMIT = getenv('SPOTPRICE_REQUEST_LIMIT', 48)

# for testing
USE_SAMPLE = getenv('USE_SAMPLE', False)
SAMPLE_FILE = getenv('SAMPLE_FILE', 'sample_response.json')

def get_spotprices(limit):
  """
  Gives the spot prices 
  """
  try:
    header = {
      "Content-Type": "application/json;charset=utf-8"
    }
    
    url = f'{SPOTPRICE_API_URL}' \
          f'resource_id=elspotprices&' \
          f'limit={limit}&' \
          f'filters={{"PriceArea":"{SPOTPRICE_AREA}"}}&' \
          f'sort=HourUTC desc'
    
    print(f"URL: {url}")

    return requests.get(url, headers=header).json()

  except Exception as ex:
      raise Exception(str(ex))

def write_to_influxdb(spotprice_records):
  '''
    Write sportprice records to influxdb
  '''
  with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for record in spotprice_records:
      # print(json.dumps(record, indent=2))
      point = Point("spotprice")
      
      point = point.tag('PriceArea', SPOTPRICE_AREA)

      kwh_price_EUR = float(record['SpotPriceEUR']) / 1000
      point = point.field('KwhEUR', kwh_price_EUR)
      point = point.field('KwhDKK', kwh_price_EUR * 7.45)

      # utc_time = record['HourUTC'].replace('+00:00', '')
      point = point.time(record['HourUTC'])

      print(f"Inserting record: {point}")

      write_api.write(INFLUXDB_BUCKET, INFLUXDB_ORG, point)


def print_csv(spotprices):
  print("--------- Start CSV output ---------")
  print("HourDK;SpotPriceKwh")
  
  for record in spotprices['result']['records']:
    kwh_price_in_DKK = float(record['SpotPriceEUR']) * 7.45 / 1000
    print(f"{record['HourDK']};{kwh_price_in_DKK}")

  print("--------- End of CSV output ---------")

if __name__ == '__main__':
  '''
      For running locally
  '''
  
  if USE_SAMPLE:
    with open(SAMPLE_FILE, 'r') as sample_file:
      spotprices = json.load(sample_file)
  else:
    spotprices = get_spotprices(SPOTPRICE_REQUEST_LIMIT)
  
  write_to_influxdb(spotprice_records=spotprices['result']['records'])
  # print(json.dumps(spotprices, indent=2))
  # print_csv(spotprices)
  