from django.db import models


class users(models.Model):
    user_id = models.IntegerField(null=True)
    file_name = models.CharField(max_length=50, null=True)


class verified(models.Model):
    user_id = models.IntegerField(null=True)
    file_name = models.CharField(max_length=50, null=True)
    value = models.CharField(max_length=10, null=True)


class result(models.Model):
    user_id = models.IntegerField(null=True)
    file_name = models.CharField(max_length=50, null=True)
    value = models.CharField(max_length=10, null=True)


class logs(models.Model):
    errors_kpi = models.CharField(max_length=60, null=True)
    errors_work = models.CharField(max_length=60, null=True)
    verified = models.CharField(max_length=60, null=True)
    SIZE = models.CharField(max_length=15, null=True)


class files(models.Model):
    file_name = models.CharField(max_length=30, null=True)

from django.db import models

# Create your models here.
