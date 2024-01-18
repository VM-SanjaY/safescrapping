from django.db import models


class Subcategory(models.Model):
    subcategory_name = models.CharField(max_length=300, blank=True, null=True)


class Datastore(models.Model):
    subcategory = models.ForeignKey(Subcategory,null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=True, null=True)
    thumb = models.ImageField(max_length=300, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    price = models.CharField(max_length=10, blank=True, null=True)
    imageurl = models.ImageField(max_length=300, blank=True, null=True)

