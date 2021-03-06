from django.db import models
from author import Author
from uuidfield import UUIDField
from ..utils.utils import ListField


class Post(models.Model):
    """
    Post
    """
    guid = UUIDField(auto=True, primary_key=True)
    title = models.CharField(blank=False, max_length=200)
    content = models.TextField(blank=False)
    contentType = models.CharField(blank=False, max_length=16)
    categories = ListField(blank=True, default=[])
    pubDate = models.DateTimeField(auto_now_add=True, editable=False)
    visibility = models.CharField(blank=False, max_length=10)
    image = models.TextField(blank=True, null=True)
    author = models.ForeignKey(Author, blank=False, editable=False)

    def __unicode__(self):
        return u'%s %s %s' % (self.author.user.username,
                              self.content, self.visibility)


class Comment(models.Model):
    """
    Comment

    A comment's privacy is inherited from the Post public attribute
    """
    guid = UUIDField(auto=True, primary_key=True)
    comment = models.TextField(blank=False)
    contentType = models.CharField(blank=True, max_length=16)
    pubDate = models.DateTimeField(auto_now_add=True, editable=False)
    post = models.ForeignKey('Post', related_name='comments')
    author = models.ForeignKey(Author, blank=False, editable=False)

    def __unicode__(self):
        return u'%s %s' % (self.author.username, self.comment)
