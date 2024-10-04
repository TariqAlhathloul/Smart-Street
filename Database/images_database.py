import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
#dataset path
csv_file_path = '../Database/violations.csv'

#read the detected violations file
df = pd.read_csv(csv_file_path)

# connect to the database
client = MongoClient(os.getenv("CONNECTION_STRING"))

# create a database and a collection
db = client['DeepLearningCluster']  
collection = db['Violations-1']  

#convert dataframe to dictionary
data = df.to_dict(orient='records')

#insert into the collection
collection.insert_many(data)

print("data inserted")

#close the connection
client.close()
#TODO: convert the above code to a function and call it in the deployment/detect.py file