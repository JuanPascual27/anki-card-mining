import os
import shutil

def create_temp_dir(name="temp"):
    rute = os.path.join(os.getcwd(), name)
    delete_temp_dir(rute)
    os.makedirs(rute, exist_ok=True)
    return rute

def delete_temp_dir(rute: str):
    if os.path.exists(rute):
        shutil.rmtree(rute)