import os
import re
import json 
import shutil
import logging
import pandas as pd
from PIL import Image
from pytesseract import pytesseract
from src.utils.common import read_yaml, create_directories


logging.basicConfig(
    filename = os.path.join("logs", 'running_logs.log'), 
    level=logging.INFO, 
    format="[%(asctime)s: %(levelname)s: %(module)s]: %(message)s",
    filemode="a"
    )


class BillExtracter:
    def __init__(self):
        pass
    

    def extract_text_from_image(self, image_path):
        # Defining paths to tesseract.exe
        path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        img = Image.open(image_path)

        # Providing the tesseract executable
        # location to pytesseract library
        pytesseract.tesseract_cmd = path_to_tesseract

        # This function will extract the text from the image
        text = pytesseract.image_to_string(img)
        logging.info(f"Text extracted from image: {image_path}")    
        return text[:-1]


    def extrat_details_from_extracted_data(self, extracted_data):
        raw_data = extracted_data.split("\n")
        entity_details = []
        customer_details = []
        item_details = []


        for line in raw_data:
            if "Customer" in line:
                idx = raw_data.index(line)
                entity_details = raw_data[0:idx]
                del raw_data[0:idx]
                break

        for line in raw_data:
            if "Item" in line:
                idx = raw_data.index(line)+1
                customer_details = raw_data[0:idx]
                del raw_data[0:idx]
                break

        for line in raw_data:
            if "Total" in line:
                idx = raw_data.index(line)
                item_details = raw_data[0:idx]
                del raw_data[0:idx]
                break
        logging.info(f"Extracted details from extracted data")
        return entity_details, customer_details, item_details, raw_data


    def create_item_details_dataframe(self, item_details):
        final_data = {"item" : [], "qty" : [], "amount" : []}

        item_details_str = ""
        for line in item_details:
            if len(line.split())>0:
                for _ in line.split():
                    item_details_str += _ + " "
        
        item_data = []
        start_idx = 0
        for i in re.finditer(r"\d+\.\d+", item_details_str):
            end_idx = i.span()[1]
            item_data.append(item_details_str[start_idx:end_idx])
            start_idx = end_idx
            
        for i in item_data:
            try:
                item = re.findall(r"[a-zA-Z\s]+", i)[0]
            except Exception as e:
                item = ""

            try:
                qty = re.findall(r"\s[0-9]\s", i)[0]
            except Exception as e:
                qty = 0

            try:
                amount = re.findall(r"[0-9]+\.[0-9]+", i)[0]
            except Exception as e:
                amount = 0

            final_data["item"].append(item)
            final_data["qty"].append(qty)
            final_data["amount"].append(amount)

        df = pd.DataFrame(final_data)
        df.to_csv("output_files\item_details.csv", index=False)
        logging.info(f"Created item details dataframe")
        return final_data
            

    def json_output(self, entity_details, customer_details, item_details, raw_data, json_file_name):
        final_data = self.create_item_details_dataframe(item_details)
        bill_data = {"entity_details" : entity_details, 
                "customer_details" : customer_details, "item_details" : final_data, "raw_data" : raw_data}
        with open(json_file_name, "w") as outfile:
            json.dump(bill_data, outfile)
        logging.info(f"Created json file: {json_file_name}")   
        return json.dumps(bill_data, indent = 4)
    