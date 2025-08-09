from django.db import models

class Course(models.Model):
    name        = models.CharField(max_length=200)
    description = models.TextField()
    category    = models.CharField(max_length=100)
    price       = models.DecimalField(max_digits=7, decimal_places=2)
    duration    = models.CharField(max_length=50)

    def __str__(self):
        return self.name
