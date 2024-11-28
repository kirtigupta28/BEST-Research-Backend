# template.py

import os
from pathlib import Path 

PROJECT_NAME = "src" #add your project name here

LIST_FILES = [
    "requirements.txt",
    "src/_init_.py",
    # config folder
    "src/config/_init_.py",
    # controllers
    "src/controllers/_init_.py",
    # middlewares
    "src/middlewares/_init_.py",
    # models
    "src/models/_init_.py",
    # routes and utils
     "src/routes.py",
     "src/utils.py",
   ]

for file_path in LIST_FILES:
    file_path = Path(file_path)
    file_dir, file_name = os.path.split(file_path)

    # first make dir
    if file_dir!="":
        os.makedirs(file_dir, exist_ok= True)
        print(f"Creating Directory: {file_dir} for file: {file_name}")
    
    if (not os.path.exists(file_path)) or (os.path.getsize(file_path)==0):
        with open(file_path, "w") as f:
            pass
            print(f"Creating an empty file: {file_path}")
    else:
        print(f"File already exists {file_path}")