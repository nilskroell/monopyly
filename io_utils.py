import os

def get_list_of_all_files(fullpath, fileending=None):
    if fileending is None:
        return os.listdir(fullpath)
    else:
        return [(fullpath/file) for file in os.listdir(fullpath) if file.endswith(fileending)]