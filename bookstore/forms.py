from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin
from django.forms import ModelForm
from bookstore.models import  Book
from django import forms





class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'author', 'category', 'pdf')
        labels = {
            'title': 'نام جزوه',
            'author': 'نام استاد',
            'category': 'دسته بندی جزوه',
            'pdf': 'فایل مورد نظر خور را اینجا بارگزاری کنید',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'author': forms.TextInput(attrs={'class':'form-control'}),
            'category': forms.Select(attrs={'class':'form-control'}),
            'pdf': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')