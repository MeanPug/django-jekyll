from django_jekyll.lib import fs
import os


class JekyllDocument(object):
    """ represents a document in a Jekyll collection """
    def __init__(self, content, filename=None, frontmatter_data=None):
        self.content = content
        self.filename = filename
        self.frontmatter_data = frontmatter_data

    def write(self, location):
        fs.write_file(self.content, os.path.join(location, self.filename + '.md'), **self.frontmatter_data)

    def __str__(self):
        return '%s (Content Length = %s, Frontmatter Data = %s)' % (self.filename, len(self.content), self.frontmatter_data)