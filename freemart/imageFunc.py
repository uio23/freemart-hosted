# Importing 3rd party components
from flask_login import current_user

import requests

from github import Github

from PIL import Image, ImageOps

from io import BytesIO

import threading

from queue import Queue

import os


# Defining jobs object
jobs = Queue()


def loadImgs(items):
    '''
        Load imgs in batches with threading
    '''

    for item in items:
        jobs.put(item.imagePath)
    for i in range(25):
        worker = threading.Thread(target=loadImg, args=(jobs,))
        worker.start()
    jobs.join()


def saveImg(productImage, imageFilename) -> bool:
    '''
        Attempt save img to repo, inform of outcome
    '''

    g = Github(os.environ.get("GITT"))
    img = Image.open(productImage)
    img = ImageOps.exif_transpose(img)
    img = img.resize((500, 500))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    for repo in g.get_user().get_repos():
        if repo.name == "freemart_img":
            repo.create_file(imageFilename, f"{current_user.username}'s uplaod", bytes(img_byte_arr), "main")
            return True
    return False


def loadImg(q):
    '''
        Load img batch
    '''

    while not q.empty():
        imageFilename = q.get()
        url = f'https://raw.githubusercontent.com/uio23/freemart_img/main/{imageFilename}'
        resp = requests.get(url)
        i = Image.open(BytesIO(resp.content))
        i.save(os.path.join(os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
                ), 'static'
                ), imageFilename))
        q.task_done()
