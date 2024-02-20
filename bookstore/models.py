from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.template.defaultfilters import filesizeformat


# User = get_user_model()


class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_publisher = models.BooleanField(default=False)
    is_librarian = models.BooleanField(default=False)

    class Meta:
        swappable = 'AUTH_USER_MODEL'



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# Modify the Book model to include a category
class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    uploaded_by = models.CharField(max_length=100, null=True, blank=True)
    user_id = models.CharField(max_length=100, null=True, blank=True)
    pdf = models.FileField(upload_to='bookapp/zips/')
    # Add a foreign key to Category
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.pdf.delete()
        if hasattr(self, 'cover'):
            self.cover.delete()
        super().delete(*args, **kwargs)
    @property
    def formatted_file_size(self):
        return filesizeformat(self.pdf.size)




class DeleteRequest(models.Model):
    delete_request = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.delete_request


class Feedback(models.Model):
    feedback = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.feedback
