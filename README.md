# spotprices

Small python script to fetch electricity spot prices from [Energi Data Service](https://www.energidataservice.dk/) using the [Elspot Prices](https://www.energidataservice.dk/tso-electricity/elspotprices) dataset for Denmark and insert in a [InfluxDB](https://www.influxdata.com/get-influxdb/) timeseries bucket.

> Note: It should be safe to run as often as you like. Deduplication in InfluxDB will ensure that identical records are only stored once.

## install

1. Create a `.env` file based on the [.env-sample](./.env-sample) and update the values to match you environment
1. Run `docker compose up -d`

## settings

Configured using environment variables, e.g., by using `.env`

- `INTERVAL="3600"`

  Wait time between script executions in seconds

- `SPOTPRICE_AREA="DK2"`

  Which area to fetch records from.
  
  Current options are:
  - DK1 (DK_WEST)
  - DK2 (DK_EAST)
  - NO2 (NO_?)
  - SE3 (SE_?)
  - SE4 (SE_?)

- `SPOTPRICE_REQUEST_LIMIT="48"`
  
  How many records to fetch. Change this to get more historical prices. The prices for next day are released at 13:00 CET, so by setting this to, e.g., 48, you're always ensured to have the current days prices in each request.
