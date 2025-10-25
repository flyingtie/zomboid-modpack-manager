from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pathlib import Path
from pydantic import AnyUrl

import click


def auth(client_secrets_path: Path = None) -> GoogleAuth:
    gauth = GoogleAuth()
    auth_url = gauth.GetAuthUrl()
    code = click.prompt(f"\n{auth_url}\n\nEnter verification code")
    gauth.Auth(code)
    
    return gauth

def upload_file(path: Path, auth: GoogleAuth) -> AnyUrl:
    if not path.exists():
        raise FileNotFoundError
    
    drive = GoogleDrive(auth)
    file = drive.CreateFile()
    file.SetContentFile(path)
    file.Upload()
    file.InsertPermission(
        {
            "type": "anyone",
            "value": "anyone",
            "role": "reader"
        }
    )
    
    return file["webContentLink"]

if __name__ == "__main__":  
    ga = auth()
    print(upload_file(Path("D:\\projects\\pyprojects\\zomboid_modpack_manager\\README.md"), ga))

# TODO:
# Добавить возможность указывать путь до client_secrets.json
# Загрузка в нужную папку
# Сканирование модов на облаке и сравнение с локальными
# 