from tortoise import fields, models


class Files(models.Model):
    filename = fields.TextField()
    path = fields.TextField()
