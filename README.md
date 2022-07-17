# Album-bot
## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Functionality](#functionality)
* [Setup](#setup)

## General info
Album bot provides basic functionality of storing images in named albums. User can save images in albums and then request the list of albums, pick one and see it's contents.

## Technologies
- Python 3.10
- Django 4.0
- Postgres 14
- Celery
- Redis
- Docker

The backend works on django and the bot runs in asynchronous
celery task. All images and data
are stored in the bot server (it doesn't rely on telegram).
Admin can see and edit albums, images through django 
admin site. 

## Functionality
###### Uploading photos
Uploading photos happens automaticaly by sending photo
to the album bot. Multiple photos at once are also supported.
Album bot then asks user what album the photo
(or a set of photos) should be added to, and saves them accordingly.
###### Retrieving the list of albums and photos
User can text or pick in the menu the "/albums" command
to request the list of all albums as a set of named 
buttons.
In this case album bot will send all images 
from that album to user as a media group (or multiple 
media groups if there are more than 10 images).
###### Show all images 
The "/showall" command privides a set of buttons
with all images stored in the album bot. Every button
is named in "album_name - image_id" format. 

## Setup

1. Install [docker-compose](https://docs.docker.com/compose/install/)
2. ```git clone https://github.com/mi-doc/telegram-bot.git && cd telegram-bot```
3. ```cat .env.sample >> .env```
4. Edit your telegram token from botfather in the .env file
5. ```docker-compose -f docker-compose.prod.yml build``` 
6. ```docker-compose -f docker-compose.prod.yml up```
7. Start the bot by going to the localhost:8000/ page