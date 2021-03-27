from apps.core.models import AbstractTime

from tortoise import fields


class Article(AbstractTime):
    id = fields.IntField(pk=True)
    author = fields.ForeignKeyField('models.User')
    title = fields.CharField(max_length=250, index=True)
    body = fields.TextField()

    class Meta:
        table = 'blog_article'

    def __str__(self):
        return self.title


class ArticleComment(AbstractTime):
    id = fields.IntField(pk=True)
    author = fields.ForeignKeyField('models.User')
    article = fields.ForeignKeyField('models.Article')
    body = fields.TextField()

    class Meta:
        table = 'blog_article_comment'

    def __str__(self):
        return self.id
