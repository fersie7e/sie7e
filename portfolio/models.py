from django.db import models


# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=100)
    subtitle= models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    git = models.CharField(max_length=200, default="")
    bg_image = models.ImageField(upload_to="images/portfolio/", null=True, blank=True, default="sie7e.png")

    def __str__(self):
        return f"{self.title}"

