from django.db import models


# Create your models here.
class Receipt(models.Model):
    retailer = models.CharField(max_length=64)
    purchaseDate = models.DateField()
    purchaseTime = models.TimeField()
    total = models.FloatField()
    points = models.FloatField()


class Items(models.Model):
    receiptId = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    shortDescription = models.CharField(max_length=256)
    price = models.FloatField()
