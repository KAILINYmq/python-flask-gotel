# coding: utf-8
"""file helper function
"""

import os
from agile.config import UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_file(dirname, filename):
    dirname = UPLOAD_FOLDER + "/" + dirname
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    return dirname + "/" + filename
