''' Utils to look for files in the filesystem respecting certain patterns. '''
import os
import fnmatch


def locate(pattern, root):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, _, files in os.walk(os.path.abspath(root)): 
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

            
def locate_roots(pattern, where):
    "where: list of files or directories where to look for pattern"
    if not(type(where) == list):
        where = [where]

    all_files = []
    for w in where:
        if not(os.path.exists(w)):
            raise ValueError("Path %s does not exist" % w)
        if os.path.isfile(w):
            all_files.append(w)
        elif os.path.isdir(w):
            all_files.extend(set(locate(pattern=pattern, root=w)))

    return all_files
 
