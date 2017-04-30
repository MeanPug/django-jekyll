import frontmatter
import shutil
import os


def write_file(content, location, **frontmatter_data):
    """
    :param content: `str` the main file content (excluding frontmatter)
    :param location: `str` path to write the file to
    :param frontmatter: `splat` of frontmatter keys / values to write to the file
    :return:
    """
    dirname = os.path.dirname(location)

    if not is_dir(dirname):
        os.makedirs(dirname)

    jekyll_post = frontmatter.Post(content, **frontmatter_data)

    with open(location, 'wb') as pfile:
        frontmatter.dump(jekyll_post, pfile)


def search_parents_for_dirs(location, for_names):
    """ traverse up the file tree, searching for `for_names` at each level.
    :param names: `list` of `str` to search for at each level of the file tree
    :return: `str` the path to the FIRST of the found for_names
    """
    dir_contents = list_dir(location)

    for name in for_names:
        name_path = os.path.join(location, name)

        if name in dir_contents and is_dir(name_path):
            return name_path

    if location == '/':
        return None
    else:
        return search_parents_for_dirs(os.path.dirname(location), for_names)


##-- Dead Simple Directory Functions --**/
def is_dir(location):
    """ check if a directory exists at the given location
    :param location:
    :return:
    """
    return os.path.isdir(location)


def remove_dir(location):
    """ remove the directory at the given location
    :param location:
    :return:
    """
    shutil.rmtree(location)


def move_dir(location, to_location):
    """ move the directory at `location` to `to_location`
    :param location:
    :param to_location:
    :return:
    """
    shutil.move(location, to_location)


def list_dir(location):
    """ list the paths of the contents of the direct children of the directory given at `location`
    :param location:
    :return:
    """
    return os.listdir(location)