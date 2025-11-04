import enum
import click
import uuid
import google.auth

from pydrive2.auth import GoogleAuth, RefreshError, AuthenticationError, InvalidCredentialsError
from pydrive2.drive import GoogleDrive
from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path
from pydantic import AnyUrl
from typing import Optional

from app.loader import GOOGLE_CREDS_PATH
from app.models import GoogleDriveFileInfo


def auth(client_secrets_path: Path = None) -> GoogleAuth:
    try:
        if not GOOGLE_CREDS_PATH.exists():
            raise FileNotFoundError
        
        gauth = GoogleAuth()
        
        gauth.LoadCredentialsFile(GOOGLE_CREDS_PATH)
        
        if gauth.access_token_expired:
            gauth.Refresh()
            gauth.SaveCredentialsFile(GOOGLE_CREDS_PATH)
            
        gauth.Authorize()
    except (RefreshError, AuthenticationError, InvalidCredentialsError, FileNotFoundError):
        settings = {
            "client_config_file": client_secrets_path,
            "get_refresh_token": True
        }
        
        gauth = GoogleAuth(settings=settings)   
            
        auth_url = gauth.GetAuthUrl()
        
        code = click.prompt(f"\n{auth_url}\n\nEnter verification code")
        
        gauth.Auth(code)
        gauth.SaveCredentialsFile(GOOGLE_CREDS_PATH)
        
    return gauth


def delete_googledrive_file(file_id: str, auth: GoogleAuth):
    drive = GoogleDrive(auth)
    
    metadata = {"id": file_id}
    
    file = drive.CreateFile(metadata=metadata)
    
    file.Delete()


def upload_file(path: Path, auth: GoogleAuth, folder_id: Optional[str] = None) -> GoogleDriveFileInfo:
    if not path.exists():
        raise FileNotFoundError
    
    drive = GoogleDrive(auth)
    
    metadata = {}
    if not not folder_id:
        metadata = {'parents': [{"id": folder_id}]}
        
    file = drive.CreateFile(metadata=metadata)
    file.SetContentFile(path)
    file.Upload()
    file.InsertPermission(
        {
            "type": "anyone",
            "value": "anyone",
            "role": "reader"
        }
    )
    
    return GoogleDriveFileInfo(
        fileid=file["id"],
        filename=file["originalFilename"],
        url=file["webContentLink"],
        filesize=file["fileSize"],
        folder_id=folder_id
    )
    
# TODO:
# Удаление файла 