import os
from roundabout import models


class Comment(dict):
    def __init__(self, comment, path):
        self._comment = comment
        self.path

    def save(self):
        comments = Comments.load(self.path)
        if self in comments:
            comments.pop(self)
        comments.append(self)
        comments.save()


class Comments(models.Model):
    __file__ = 'comments.js'
    __inner__ = Comment

    def __init__(self, comments, path):
        self.index = 0
        self.comments = comments
        self.filename = os.path.join(path, self.__file__)

    def __iter__(self):
        return self

    def next(self):
        try:
            res = self.comments[self.index]
        except IndexError:
            raise StopIteration
        self.index += 1
        return res

    def save(self):
        super(Comments, self).save(self.comments)
