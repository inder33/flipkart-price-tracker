import csv
import os
import asyncio
import random

from datetime import datetime
from scraper import get_id_json_data


file_name = "csv_data/data.csv"

# 🕒 Freeze the timestamp EXACTLY when the script starts running!
RUN_TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M")
DYNAMIC_CHANGES_FILE = f"csv_data/changes_{RUN_TIMESTAMP}.csv"

#----------------------------------------------------------------[ PRINT DATA ON TERMINAL ]
def print_json_data(data):

    print(f"sku = {data[0]["sku"]}")
    print(f"name = {data[0]["name"]}")
    print(f"color = {data[0]["color"]}")
    print(f"ratings = {data[0]["ratings"]}")
    print(f"price = {data[0]["price"]}")
    print(f"price currency = {data[0]["priceCurrency"]}")
    print(f"Availability = {data[0]["availability"]}")

    print("=========================================")

#------------------------------------------------------------------[ SAVE DATA TO BOTH OUTSTOCK/INSTOCK CSV ]

def save_to_csv(headers, data , pass_value):

    if pass_value == 1:
        with open("csv_data/data.csv" , "a" , newline="" , encoding="utf-8") as file:
            writer = csv.DictWriter(file , fieldnames=headers)

            if file.tell() == 0:
                writer.writeheader()

            writer.writerow({
                "sku" : data[0]["sku"],
                "name" : data[0]["name"],
                "color" : data[0]["color"],
                "ratings" : data[0]["ratings"],
                "price" : data[0]["price"],
                "price currency" : data[0]["priceCurrency"],
                "Availability" : data[0]["availability"]
            })

    elif pass_value == 2:
        with open("csv_data/InStock_items.csv" , "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)

            if file.tell() == 0:
                writer.writeheader()

            writer.writerow({
                "sku": data["sku"],
                "name" : data["name"],
                "color" : data["color"],
                "ratings" : data["ratings"],
                "price" : data["price"],
                "price currency" : data["price currency"],
                "Availability" : data["Availability"]
            })

#--------------------------------------------------------------------------------[ IN-STOCK DATA CHECKER ]

def In_stock_items(data):
    headers = ["sku","name","color","ratings","price","price currency", "Availability"]

    stock = data[0]["availability"]

    if stock == "InStock":
        instock = {
            "sku" : data[0]["sku"],
            "name" : data[0]["name"],
            "color" : data[0]["color"],
            "ratings" : data[0]["ratings"],
            "price" : data[0]["price"],
            "price currency" : data[0]["priceCurrency"],
            "Availability" : data[0]["availability"]
            }
        
        save_to_csv(headers,instock,pass_value=2)

#---------------------------------------------------------------------------------[ DUPLICATE - PRODUCT CHECKER ]

def Duplicate_sku_checker(data):
    if os.path.isfile(file_name):
        current_sku = data[0]["sku"]
        with open("csv_data/data.csv", 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["sku"] == current_sku:
                    change = price_change_checker(row,data)
                    if change == None:
                        return {"value": False , "change" : None, "total_changes": 0}
                    
                    if change["change"] == "price droped":
                        total_rows = modify_csv_list(current_sku, change["current_price"])
                        return {"value": False, "change" : change["change"], "total_changes" : total_rows}

                    if change["change"] == "price increased":
                        total_rows = modify_csv_list(current_sku , change["current_price"])
                        return {"value": False, "change" : change["change"], "total_changes" : total_rows}
            
            return {"value":True, "change" : None, "total_changes": 0}
    else:
        return {"value":True, "change" : None, "total_changes": 0}

#---------------------------------------------------------------------------------[ PRICE CHANGE CHECKER ]

def price_change_checker(row_data,data):

    old_price = row_data["price"]
    current_price = data[0]["price"]

    if int(old_price) > int(current_price):
        print("price droped!")
        change = "price droped"
        final_price = int(old_price) - int(current_price)
        return {
            "change" : change , 
            "current_price" : int(current_price),
            "final_price" : final_price
            }

    elif int(current_price) > int(old_price):
        print("price increased ")
        change = "price increased"
        final_price = int(current_price) - int(old_price)
        return {
            "change" : change, 
            "current_price" : int(current_price),
            "final_price" : final_price
            }

    else:
        return None

#-----------------------------------------------------------------------[ MODIFY CVS LIST WHRE PRICE CHANGE ]

def modify_csv_list(sku , change):
    with open("csv_data/data.csv" ,"r",newline="" , encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

        file_info = {"count": 0, "filename": None}

        count = 0
        for row in rows:
            if row["sku"] == sku:
                old_price = row["price"]
                row["price"] = change
                file_info = save_price_change(row["sku"],old_price,row["price"])
                count += 1

    with open("csv_data/data.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Price updated for {count} products ")

    return file_info

async def scrape_product(page, link , headers ):
    current_log_count = 0
    try :
        await page.goto("https://www.flipkart.com"+ link , wait_until="domcontentloaded")
        await asyncio.sleep(random.uniform(0.1,0.7))

        data = await get_id_json_data(page)
        changes = Duplicate_sku_checker(data)

        if changes["value"] == True:
            save_to_csv(headers,data, pass_value=1)
            print_json_data(data)
            In_stock_items(data)
            return 0 

        elif changes["change"] in ["price droped", "price increased"]:
            print(f"{changes['change']} , Csv updated !")
            # Pull out the total_changes number we just fixed above
            current_log_count = changes.get("total_changes", 0) 
            return current_log_count

        else:
            print("Product Already in CSV Skipped !")
            return 0
    
    except Exception as e:
        print(f"Skipped — {e}")
        return 0

def save_price_change(passed_sku , old_price , new_price):
    updated_headers = ["sku","name","color","ratings","oldPrice","newPrice" ,"price_currency","Availability"]

    with open("csv_data/data.csv" ,"r",newline="" , encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

        data = {}
        for row in rows:
            if row["sku"] == passed_sku:
                data = {
                    "sku" : row["sku"],
                    "name": row["name"],
                    "color": row["color"],
                    "ratings" :row["ratings"],
                    "oldPrice":old_price,
                    "newPrice" :new_price,
                    "price_currency": row["price currency"],
                    "Availability" :row["Availability"]
                }

        os.makedirs("csv_data", exist_ok=True)

    # 🔒 Uses the frozen file path, no matter how many minutes pass!
    with open(DYNAMIC_CHANGES_FILE , "a" , newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file , fieldnames=updated_headers)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(data)
        
    with open(DYNAMIC_CHANGES_FILE, "r", encoding="utf-8") as file:
        total_rows = len(file.readlines()) - 1
        
    return total_rows
