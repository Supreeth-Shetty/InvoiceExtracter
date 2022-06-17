import os
import logging
from src.bill_extracter_helper import BillExtracter

STAGE = "main stage" 

logging.basicConfig(
    filename=os.path.join("logs", 'running_logs.log'), 
    level=logging.INFO, 
    format="[%(asctime)s: %(levelname)s: %(module)s]: %(message)s",
    filemode="a"
    )


def main():
    extracter = BillExtracter()
    extracted_data = extracter.extract_text_from_image("test_images/photo6136222383296589771.jpg")
    entity_details, customer_details, item_details, raw_data = extracter.extrat_details_from_extracted_data(extracted_data)
    json_data = extracter.json_output(entity_details, customer_details, item_details, raw_data, "sample.json")
    print(json_data)

if __name__ =="__main__":
    try:
        logging.info("\n********************")
        logging.info(f">>>>> stage {STAGE} started <<<<<")
        main()
        logging.info(f">>>>> stage {STAGE} completed!<<<<<\n")
    except Exception as e:
        logging.exception(e)
        raise e