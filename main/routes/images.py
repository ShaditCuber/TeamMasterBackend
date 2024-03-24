from fastapi import APIRouter
from datetime import datetime
from zipfile import ZipFile
import random
import os
import requests
import boto3

router = APIRouter()


def get_zip_avatars_(persons: list, name):

    local_folder = "/tmp"
    local_file_zip = f"{local_folder}/avatars-{name}.zip"
    local_file_path = f"{local_folder}/{name}"

    s3 = boto3.client("s3")
    os.makedirs(local_file_path, exist_ok=True)

    for person in persons:

        person_name_camel_case = person["name"].replace(" ", "_").lower()
        path = (
            f"{local_file_path}/{person['registrantId']}_{person_name_camel_case}.jpg"
        )
        with open(
            path,
            "wb",
        ) as file:
            file.write(requests.get(person["url"]).content)

    with ZipFile(local_file_zip, "w") as zip:
        for root, dirs, files in os.walk(local_file_path):
            print(root, dirs, files)
            for file in files:
                zip.write(os.path.join(root, file), file)

    # nombre del zip que sea avatars + fecha
    name_zip = f"avatars-{name}.zip"

    s3.upload_file(
        local_file_zip,
        "avatars-images",
        name_zip,
    )

    # Eliminar archivos locales
    # os.remove(local_file_path)
    # os.remove(local_file_zip)
    # borrar el directorio con los archivos
    for root, dirs, files in os.walk(local_file_path):
        for file in files:
            os.remove(os.path.join(root, file))

    # Borrar el zip
    os.remove(local_file_zip)

    # Generar url para el usuario
    return f"https://avatars-images.s3.amazonaws.com/{name_zip}"


@router.post("/getAvatarsZip")
def get_zip_avatars(avatars: dict):

    avatars = avatars["avatars"]

    # sacar el ultimo y obtener el name
    name = avatars.pop(-1)["name"]

    url_zip = get_zip_avatars_(avatars, name)
    return {
        "url": url_zip,
    }
