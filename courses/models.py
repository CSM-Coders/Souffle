from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    name        = models.CharField(max_length=200)
    description = models.TextField()
    category    = models.CharField(max_length=100)
    price       = models.DecimalField(max_digits=6, decimal_places=2)
    date        = models.DateField()
    duration    = models.CharField(max_length=50)
    image       = models.ImageField(upload_to='courses/', blank=True)

    def __str__(self):
        return self.name

class Schedule(models.Model):
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    start_time = models.DateTimeField()
    quota      = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.course.name} – {self.start_time}"

class Reservation(models.Model):
    user       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    email      = models.EmailField()
    schedule   = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} – {self.schedule}"
