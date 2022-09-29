# Fetches data from https://www.energidataservice.dk/tso-electricity/elspotprices
# API documentation http://docs.ckan.org/en/latest/api/index.html#making-an-api-request

import time, json
import requests
from os import getenv, pipe
from datetime import datetime
from dateutil.parser import parse
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import *

INFLUXDB_TOKEN = getenv('INFLUXDB_TOKEN', None)
INFLUXDB_ORG = getenv('INFLUXDB_ORG', None)
INFLUXDB_BUCKET = getenv('INFLUXDB_BUCKET', 'default')
INFLUXDB_URL = getenv('INFLUXDB_URL', 'http://localhost:8086')

POSTGRES_USER = getenv('POSTGRES_USER', "postgres")
POSTGRES_PASSWORD = getenv('POSTGRES_PASSWORD', "")
POSTGRES_HOST = getenv('POSTGRES_HOST', 'db')
POSTGRES_DB = getenv('POSTGRES_DB', 'spotprice')

SPOTPRICE_API_URL = "https://api.energidataservice.dk/dataset/"

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
    # API sample request
    # https://api.energidataservice.dk/dataset/Elspotprices?limit=2400&filter={"PriceArea":"DK2"}&sort=HourUTC%20desc
    url = f'{SPOTPRICE_API_URL}' \
          f'Elspotprices?' \
          f'limit={limit}&' \
          f'filter={{"PriceArea":"{SPOTPRICE_AREA}"}}&' \
          f'sort=HourUTC%20desc'
    # print(f"URL: {url}")
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
  
  for record in spotprices['records']:
    kwh_price_in_DKK = float(record['SpotPriceEUR']) * 7.45 / 1000
    print(f"{record['HourDK']};{kwh_price_in_DKK}")

  print("--------- End of CSV output ---------")

def db_connect(return_engine=False):
  db_url =(
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}/{POSTGRES_DB}"
  )
  engine = create_engine(db_url)

  if return_engine:
    return engine
  else:
    Session = sessionmaker()
    Session.configure(bind=engine)
    return Session()

if __name__ == '__main__':
  '''
      For running locally
  '''
  
  if USE_SAMPLE:
    with open(SAMPLE_FILE, 'r') as sample_file:
      spotprices = json.load(sample_file)
  else:
    spotprices = get_spotprices(SPOTPRICE_REQUEST_LIMIT)
  
  # write_to_influxdb(spotprice_records=spotprices['records'])

  # print(json.dumps(spotprices, indent=2))
  # print_csv(spotprices)
  # with open('output.json', 'w') as outfile:
  #   json.dump(spotprices['records'], outfile, indent=4)
  
  db = db_connect(return_engine=True)
  Base.metadata.create_all(db)
