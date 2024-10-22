"""
fetch data from the database
and store it in a text file to push it into a vector store
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()


#make a directory to store the violations in a txet file
dir = "./violations_descriptsion_arabic"
os.makedirs(dir, exist_ok=True)

#establish connection to the database
client = MongoClient(os.getenv('CONNECTION_STRING'))

db = client['DeepLearningCluster']  
collection = db['Violations-1']  

#retrieve all the documents from the database
documents = collection.find()

# Iterate over documents and create a text file for each
for i, document in enumerate(documents):
    # Prepare the text content from document fields
    text = (
f"""{document.get('time')} تم رصد مخالفة مرورية في الوقت 
{document.get('date') } في التاريخ الموافق 
{document.get('latitude')}, {document.get('longitude')} احداثيات المخالفة 
{document.get('violation_type')}  نوع المخالفة 
{document.get('license_plate_number')} رقم اللوحه
{document.get('vehicle_type')} نوع المركبة
اسم الطريق {document.get('street_name')} 
{i}رقم المخالفة""")
    
    # write to text file
    with open(os.path.join(dir, f'text{i}.txt'), 'w') as file:
        file.write(text)

