from django_jekyll.lib import fs


class Document(object):
    """ represents a document in a Jekyll collection """
    def __init__(self, content, filename=None, frontmatter_data=None):
        self.content = content
        self.filename = filename
        self.frontmatter_data = frontmatter_data

    def write(self, location):
        fs.write_file(self.content, location, **self.frontmatter_data)