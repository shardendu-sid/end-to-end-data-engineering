import json
import requests
import os
import csv 

API_KEY = os.environ.get("marketstackapi_keys")
url = os.environ.get("marketstackurl") # /v1/eod,/v1/tickers,/v1/exchanges,/v1/intraday

csv_path = "/Users/shardendujha/Documents/End-to-End_Data_eng_Project/database/financial_market_data.csv"
c_columns = ['open','high','low','close','volume','adj_high','adj_low','adj_close','adj_open','adj_volume',
                 'split_factor', 'dividend','symbol','exchange', 'date']

def gloabal_financial_market_data():
 
   

    params = {
                "access_key": API_KEY,
                "symbols": "AAPL",
                "limit": 5
            }
    response = requests.get(url, params=params)
    data = response.json()
    data.pop('pagination', None)

    dict_data = []
    for i in data.items():
        for row in i[1]:
            dict_data.append(row)

    if os.path.exists(csv_path):
        existing_rows = []
        with open(csv_path, "r") as read_file:
            reader = csv.DictReader(read_file)

            for row in reader:
                existing_rows.append(row)

        with open(csv_path, "a+", newline="") as add_obj:
            writer = csv.DictWriter(add_obj, fieldnames=c_columns)


            for row in dict_data:
                if row in existing_rows:
                    print(
                        "This record already exists. You cannot make it a duplicate."
                    )
                else:
                    writer.writerow(row)
    else:
        try:
            with open(csv_path, "w", newline="") as write_file:
                writer = csv.DictWriter(write_file, fieldnames=c_columns)
                writer.writeheader()

                for row_data in dict_data:
                    writer.writerow(row_data)
        except ValueError:
            print("I/O Error")
                
    

    json_path = "/Users/shardendujha/Documents/End-to-End_Data_eng_Project/database/financial_market_data.json"
    if os.path.exists(json_path):
        with open(json_path) as j_file:
            existing_record = json.load(j_file)

        for record in dict_data:
            if record in existing_record:
                print("This record is already exist. You can not make it duplicate")
            else:
                with open(json_path, "w") as r_json:
                    json.dump(existing_record, r_json, sort_keys=True, indent=4)
    else:
        with open(json_path, "w") as write_json:
            json.dump(dict_data, write_json, sort_keys=True, indent=4)

            # print(value)
gloabal_financial_market_data()
