
# -*- coding: utf-8 -*-
"""
Created on Thursday, November 11, 2021
Find files created in the last 24 hours, copies them to a zip archive,
    and backups the zip on Drive.
@author: Mark Laubach
"""

# instructions for connecting to Drive and code for file access is from:
# https://medium.com/analytics-vidhya/how-to-connect-google-drive-to-python-using-pydrive-9681b2a14f20

# how to remove browser dependence after first authentification
# https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process

# code for finding files is from:
# https://gist.github.com/MatthewAndres/25719ef89622f6666fa5

# pydrive2 was installed using conda: conda install -c conda-forge pydrive2

# IMPORTANT: an API key from Google Drive must be available in the folder where this code is run
#  name must be client_secrets.json

import glob, os, datetime, shutil
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# authentication with Google
gauth = GoogleAuth()
#gauth.LocalWebserverAuth()

# https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process
# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")

# create a local instance of Google Drive
drive = GoogleDrive(gauth)

# paths for local files and where to put them on Drive
# change SET PATH HERE to your path
originPath = "SET PATH HERE"  # where the files are on the local machine
destinationPath = "SET PATH HERE"  # temp directory for zipping files

# Create list of filenames in origin folder defined by the extension (fileType)
#fileList = glob.glob(originPath + "!*") # MedPC data files start with !
# change FILE EXTENSION to your file type
# this seems expandable to multiple file types with some editing
# *.* would grab all files
fileList = glob.glob(originPath + "*.FILE EXTENSION")

for file in fileList:
    # Get last modified date and today's date
    modifyDate = datetime.datetime.fromtimestamp(os.path.getmtime(file))
    todaysDate = datetime.datetime.today()
    
    filePathList = file.split("\\") # Create a list from the filepath
    filename = filePathList[-1] # The last element is the filename
    
    # If modified within last 24 hours, then copy to destination folder
    modifyDateLimit = modifyDate + datetime.timedelta(days=1)

    # If the file was edited less then 24 hours ago then copy it
    # importantly, this COPIES and does not MOVE  - ML
    if modifyDateLimit > todaysDate:
        shutil.copy2(file, destinationPath)

# zip the folder - added by ML
archive = datetime.date.today().strftime('%Y-%m-%d')
shutil.make_archive(originPath + archive, 'zip', destinationPath)
# update the file name
archive = archive + ".zip"

# copy archive to current working directory
#  done to eliminate need for keeping path name in file for transfer to Drive
#  -> there is probably a better way to do this
#  copy2 is used to preserve timestamp on file
shutil.copy2(originPath + archive, os.getcwd())

# copy the archive to Drive
backup = drive.CreateFile()
backup.SetContentFile(archive)
backup.Upload()

# remove the zipped archives
os.remove(originPath + archive) # original location
os.remove(archive) # working directory

cleanup = glob.glob(destinationPath + '/!*') # list files in temp dir
for i in cleanup:
    os.remove(i) # remove them

