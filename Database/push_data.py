import pymongo
from pymongo import MongoClient
import gridfs
import os
from dotenv import load_dotenv


#the directory where the violation images are stored
dir = '../resources/violation_images'
#the directory where the retrived images are stored
retrive_dir = '../resources/retrived_images'

#load the environment variables
load_dotenv()
#start the connection
client = MongoClient(os.getenv("CONNECTION_STRING"))
db = client['DeepLearningCluster']
fs = gridfs.GridFS(db)

def push_image_to_database():
    """
    the function pushes violation car images to the database.
    """
    #push the images to the database
    for image in os.listdir(dir):
        with open(f"{dir}/{image}", "rb") as image:
            fs.put(image, filename=image.name)

def retrive_image_from_database():
    """
    the function retrives images from the database.
    """
    #retrive the images
    for image in fs.find():
        with open(f"{retrive_dir}/{image.filename}", "wb") as retrived_image:
            retrived_image.write(image.read())

