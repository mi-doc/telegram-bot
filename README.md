# Album-bot
## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Functionality](#functionality)
* [Setup](#setup)

## General info
Album bot allows to upload an image or a set of images 
in order to save them in named albums. User can request
a list of albums, and pick one to see all 
its images. 

## Technologies
- Python 3.10
- Django 4.0
- Postgres 14
- Celery
- Redis
- Docker

The backend works on django and bot runs in asynchronous
celery task. All images and data
are stored in bot server (it doesn't rely on telegram).
Admin can see and edit albums, images on django 
admin site. 

## Functionality
###### Uploading photos
Uploading photos happens automatically by sending photo
to the album bot. Multiple photos at once also supported.
Album bot then asks user what album to add the photo
(or a set of photos) to, and saves them accordingly.
###### Retrieving list of albums and photos
User can text or pick in menu the "/albums" command
to request the list of all albums as a set of named 
buttons.
After pressing a button album bot will send all images 
from that album to user as a media group.
###### Show all images 
The "/showall" command is used to get a set of buttons
with all images stored in the album bot. Every button
is named in "album_name - image_id" format. 

## Setup

1. Install [docker-compose](https://docs.docker.com/compose/install/)
2. ```git clone https://github.com/mi-doc/telegram-bot.git && cd emarket```
3. ```cat .env.sample >> .env```
4. Specify your telegram token from botfather in .env file
5. ```docker-compose -f docker-compose.dev.yml build``` 
6. ```docker-compose -f docker-compose.dev.yml up```

