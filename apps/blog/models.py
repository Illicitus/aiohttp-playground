from apps.core.models import AbstractTime
from core.serializers.main import PydanticSerializer

from tortoise import fields


class Article(AbstractTime):
    id = fields.IntField(pk=True)
    author = fields.ForeignKeyField('models.User')
    title = fields.CharField(max_length=250, index=True)
    body = fields.TextField()

    class Meta:
        table = 'blog_article'

    def __str__(self) -> str:
        return self.title


class ArticleComment(AbstractTime):
    id = fields.IntField(pk=True)
    author = fields.ForeignKeyField('models.User')
    article = fields.ForeignKeyField('models.Article')
    body = fields.TextField()

    class Meta:
        table = 'blog_article_comment'

    def __str__(self) -> int:
        return self.id


ArticlePydantic = PydanticSerializer(Article)
ArticleCommentPydantic = PydanticSerializer(ArticleComment)
