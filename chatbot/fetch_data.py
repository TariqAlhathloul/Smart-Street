"""
fetch data from the database
"""

import os
from dotenv import load_dotenv
load_dotenv()
#make a directory to store the violations in a txet file
dir = "./violations_descriptsion_arabic"
os.makedirs(dir, exist_ok=True)


from pymongo import MongoClient

#establish connection to the database
client = MongoClient(os.getenv('CONNECTION_STRING'))

db = client['DeepLearningCluster']  
collection = db['Violations-1']  

#retrieve all the documents from the database

documents = collection.find()

# Iterate over documents and create a text file for each
for i, document in enumerate(documents):
    # Prepare the text content from document fields
    text = (f"تم رصد مخالفة مرورية في الوقت {document.get('time') } في التاريخ الموافق {document.get('date') } احداثيات المخالفة {document.get('latitude')}, {document.get('longitude')} نوع المخالفة {document.get('violation_type')} رقم اللوحة {document.get('license_plate_number')} نوع المركبة {document.get('vehicle_type')} في طريق {document.get('street_name')}")
    with open(os.path.join(dir, f'text{i}.txt'), 'w') as file:
        file.write(text)

