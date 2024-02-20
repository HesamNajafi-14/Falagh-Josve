from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import generic
from bootstrap_modal_forms.mixins import PassRequestMixin
from .models import User, Book , DeleteRequest, Feedback, Category
from django.contrib import messages
from django.db.models import Sum
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView
from .forms import UserForm ,BookForm
from . import models
import operator
import itertools
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, logout
from django.contrib import auth, messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from os.path import splitext
class CategoryListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'publisher/category_list.html'
    context_object_name = 'books'

    def get_queryset(self):
        category_name = self.kwargs['foo'].replace('-', ' ')
        self.category = get_object_or_404(Category, name=category_name)
        return Book.objects.filter(category=self.category).order_by("id")

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context

    def handle_no_permission(self): 
        messages.error(self.request, "همچین رشته تحصیلی وجود ندارد")
        return redirect('publisher')


class AsliListCategory(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'publisher/asli.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'categories'
    paginate_by=10

# Shared Views
def login_form(request):
    if request.user.is_authenticated == True:
        return redirect('publisher')
    return render(request, 'bookstore/login.html')


def logoutView(request):
    logout(request)
    return redirect('home')


def loginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            if user.is_admin or user.is_superuser:
                return redirect('dashboard')
            elif user.is_librarian:
                return redirect('librarian')
            else:
                return redirect('publisher')
        else:
            messages.info(request, "نام کاربری یا رمز عبور اشتباه می باشد")
            return redirect('home')


def register_form(request):
    return render(request, 'bookstore/register.html')


def registerView(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password = make_password(password)

        a = User(username=username, email=email, password=password)
        a.save()
        messages.success(request, 'اکانت شما با موفقیت ساخته شد')
        return redirect('home')
    else:
        messages.error(request, 'ثبت نام ناموفق لطفا دوباره امتحان کنید')
        return redirect('regform')


# Publisher views
#@login_required
#def publisher(request):
    #return render(request, 'publisher/home.html')

class AddBookView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'publisher/add_book.html'
    #fields = ('title', 'author', 'category', 'pdf')


@login_required
def uabook_form(request):
    return render(request, 'publisher/add_book.html')


@login_required
def request_form(request):
    return render(request, 'publisher/delete_request.html')


@login_required
def feedback_form(request):
    return render(request, 'publisher/send_feedback.html')


@login_required
def about(request):
    return render(request, 'publisher/about.html')


@login_required
def usearch(request):
        if request.method == "POST":
            query = request.POST['query']
            books = Book.objects.filter(title__icontains=query).order_by("id")

            return render(request, 'publisher/result.html', {'query': query, 'books': books})
        else:
            messages.error(request, 'همچین جزوه ای در دیتابیس وجود ندارد')
            return redirect('publisher')


@login_required
def delete_request(request):
    if request.method == 'POST':
        book_id = request.POST['delete_request']
        current_user = request.user
        user_id = current_user.id
        username = current_user.username
        user_request = username + "  want book with id  " + book_id + " to be deleted"

        a = DeleteRequest(delete_request=user_request)
        a.save()
        messages.success(request, 'Request was sent')
        return redirect('request_form')
    else:
        messages.error(request, 'Request was not sent')
        return redirect('request_form')


@login_required
def send_feedback(request):
    if request.method == 'POST':
        feedback = request.POST['feedback']
        current_user = request.user
        user_id = current_user.id
        username = current_user.username
        feedback = username + " " + " says " + feedback

        a = Feedback(feedback=feedback)
        a.save()
        messages.success(request, 'Feedback was sent')
        return redirect('feedback_form')
    else:
        messages.error(request, 'Feedback was not sent')
        return redirect('feedback_form')


class UBookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'publisher/book_list.html'
    context_object_name = 'books'
    paginate_by = 10

    def get_queryset(self):
        return Book.objects.order_by('id')



@login_required
def uabook(request):
    choices = Category.objects.all().values_list('name', 'name')
    choice_list = []
    for item in choices:
        choice_list.append(item) 

    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        category_id = request.POST['category']
        pdf = request.FILES['pdf']

        # چک کردن پسوند فایل
        _, file_extension = splitext(pdf.name)
        allowed_extensions = ['.zip', '.rar']

        if file_extension.lower() not in allowed_extensions:
            messages.error(request, 'دوست عزیز لطفا فایل را در قالب .zip یا .rar ارسال کنید')
            return redirect('publisher')

        current_user = request.user
        user_id = current_user.id
        username = current_user.username

        a = Book(title=title, author=author,
                 pdf=pdf, uploaded_by=username, user_id=user_id, category_id=category_id)
        a.save()
        messages.success(request, 'جزوه شما با موفقیت اضافه شد')
        return redirect('publisher')
    else:
        return render(request, 'publisher/add_book.html', {'categories': choice_list})  # Pass choice_list as categories to the template







# Librarian views
def librarian(request):
    book = Book.objects.all().count()
    user = User.objects.all().count()

    context = {'book': book, 'user': user}

    return render(request, 'librarian/home.html', context)


@login_required
def labook_form(request):
    return render(request, 'librarian/add_book.html')


@login_required
def labook(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        
        pdf = request.FILES['pdf']
        current_user = request.user
        user_id = current_user.id
        username = current_user.username

        a = Book(title=title, author=author,
                 pdf=pdf, uploaded_by=username, user_id=user_id)
        a.save()
        messages.success(request, 'فایل شما با موفقیت ثبت گردید')
        return redirect('llbook')
    else:
        messages.error(request, 'فایل شما ثبت نگردید')
        return redirect('llbook')


class LBookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'librarian/book_list.html'
    context_object_name = 'books'
    paginate_by = 5

    def get_queryset(self):
        return Book.objects.order_by('-id')


class LManageBook(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'librarian/manage_books.html'
    context_object_name = 'books'
    paginate_by = 3

    def get_queryset(self):
        return Book.objects.order_by('-id')


class LDeleteRequest(LoginRequiredMixin, ListView):
    model = DeleteRequest
    template_name = 'librarian/delete_request.html'
    context_object_name = 'feedbacks'
    paginate_by = 3

    def get_queryset(self):
        return DeleteRequest.objects.order_by('-id')


class LViewBook(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'librarian/book_detail.html'


class LEditView(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'librarian/edit_book.html'
    success_url = reverse_lazy('lmbook')
    success_message = 'Data was updated successfully'


class LDeleteView(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = 'librarian/confirm_delete.html'
    success_url = reverse_lazy('lmbook')
    success_message = 'Data was deleted successfully'


class LDeleteBook(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = 'librarian/confirm_delete2.html'
    success_url = reverse_lazy('librarian')
    success_message = 'Data was dele successfully'


@login_required
def lsearch(request):
    query = request.GET['query']
    print(type(query))

    # data = query.split()
    data = query
    print(len(data))
    if (len(data) == 0):
        return redirect('publisher')
    else:
        a = data

        # Searching for It
        qs5 = models.Book.objects.filter(id__iexact=a).distinct()
        qs6 = models.Book.objects.filter(id__exact=a).distinct()

        qs7 = models.Book.objects.all().filter(id__contains=a)
        qs8 = models.Book.objects.select_related().filter(id__contains=a).distinct()
        qs9 = models.Book.objects.filter(id__startswith=a).distinct()
        qs10 = models.Book.objects.filter(id__endswith=a).distinct()
        qs11 = models.Book.objects.filter(id__istartswith=a).distinct()
        qs12 = models.Book.objects.all().filter(id__icontains=a)
        qs13 = models.Book.objects.filter(id__iendswith=a).distinct()

        files = itertools.chain(qs5, qs6, qs7, qs8, qs9, qs10, qs11, qs12, qs13)

        res = []
        for i in files:
            if i not in res:
                res.append(i)

        # word variable will be shown in html when user click on search button
        word = "Searched Result :"
        print("Result")

        print(res)
        files = res

        page = request.GET.get('page', 1)
        paginator = Paginator(files, 10)
        try:
            files = paginator.page(page)
        except PageNotAnInteger:
            files = paginator.page(1)
        except EmptyPage:
            files = paginator.page(paginator.num_pages)

        if files:
            return render(request, 'librarian/result.html', {'files': files, 'word': word})
        return render(request, 'librarian/result.html', {'files': files, 'word': word})





# Admin views

def dashboard(request):
    book = Book.objects.all().count()
    user = User.objects.all().count()

    context = {'book': book, 'user': user}

    return render(request, 'dashboard/home.html', context)


def create_user_form(request):
    choice = ['1', '0', 'Publisher', 'Admin', 'Librarian']
    choice = {'choice': choice}

    return render(request, 'dashboard/add_user.html', choice)


class ADeleteUser(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'dashboard/confirm_delete3.html'
    success_url = reverse_lazy('aluser')
    success_message = "Data successfully deleted"


class AEditUser(SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'dashboard/edit_user.html'
    success_url = reverse_lazy('aluser')
    success_message = "Data successfully updated"


class ListUserView(generic.ListView):
    model = User
    template_name = 'dashboard/list_users.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        return User.objects.order_by('-id')


def create_user(request):
    choice = ['1', '0', 'Publisher', 'Admin', 'Librarian']
    choice = {'choice': choice}
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        userType = request.POST['userType']
        email = request.POST['email']
        password = request.POST['password']
        password = make_password(password)
        print("User Type")
        print(userType)
        if userType == "Publisher":
            a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password,
                     is_publisher=True)
            a.save()
            messages.success(request, 'Member was created successfully!')
            return redirect('aluser')
        elif userType == "Admin":
            a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password,
                     is_admin=True)
            a.save()
            messages.success(request, 'Member was created successfully!')
            return redirect('aluser')
        elif userType == "Librarian":
            a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password,
                     is_librarian=True)
            a.save()
            messages.success(request, 'Member was created successfully!')
            return redirect('aluser')
        else:
            messages.success(request, 'Member was not created')
            return redirect('create_user_form')
    else:
        return redirect('create_user_form')


class ALViewUser(DetailView):
    model = User
    template_name = 'dashboard/user_detail.html'





@login_required
def aabook_form(request):
    return render(request, 'dashboard/add_book.html')


@login_required
def aabook(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.uploaded_by = request.user.username
            book.user_id = request.user.id
            book.save()
            messages.success(request, 'Book was uploaded successfully')
            return redirect('albook')
        else:
            messages.error(request, 'Book was not uploaded successfully')
            return redirect('aabook_form')
    else:
        form = BookForm()
        return render(request, 'aabook_form.html', {'form': form})


class ABookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'dashboard/book_list.html'
    context_object_name = 'books'
    paginate_by = 5

    def get_queryset(self):
        return Book.objects.order_by('-id')


class AManageBook(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'dashboard/manage_books.html'
    context_object_name = 'books'
    paginate_by = 5

    def get_queryset(self):
        return Book.objects.order_by('-id')


class ADeleteBook(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = 'dashboard/confirm_delete2.html'
    success_url = reverse_lazy('ambook')
    success_message = 'Data was dele successfully'


class ADeleteBookk(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = 'dashboard/confirm_delete.html'
    success_url = reverse_lazy('dashboard')
    success_message = 'Data was dele successfully'


class AViewBook(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'dashboard/book_detail.html'


class AEditView(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'dashboard/edit_book.html'
    success_url = reverse_lazy('ambook')
    success_message = 'Data was updated successfully'


class ADeleteRequest(LoginRequiredMixin, ListView):
    model = DeleteRequest
    template_name = 'dashboard/delete_request.html'
    context_object_name = 'feedbacks'
    paginate_by = 3

    def get_queryset(self):
        return DeleteRequest.objects.order_by('-id')


class AFeedback(LoginRequiredMixin, ListView):
    model = Feedback
    template_name = 'dashboard/feedback.html'
    context_object_name = 'feedbacks'
    paginate_by = 3

    def get_queryset(self):
        return Feedback.objects.order_by('-id')


@login_required
def asearch(request):
    query = request.GET['query']
    print(type(query))

    # data = query.split()
    data = query
    print(len(data))
    if (len(data) == 0):
        return redirect('dashborad')
    else:
        a = data

        # Searching for It
        qs5 = models.Book.objects.filter(id__iexact=a).distinct()
        qs6 = models.Book.objects.filter(id__exact=a).distinct()

        qs7 = models.Book.objects.all().filter(id__contains=a)
        qs8 = models.Book.objects.select_related().filter(id__contains=a).distinct()
        qs9 = models.Book.objects.filter(id__startswith=a).distinct()
        qs10 = models.Book.objects.filter(id__endswith=a).distinct()
        qs11 = models.Book.objects.filter(id__istartswith=a).distinct()
        qs12 = models.Book.objects.all().filter(id__icontains=a)
        qs13 = models.Book.objects.filter(id__iendswith=a).distinct()

        files = itertools.chain(qs5, qs6, qs7, qs8, qs9, qs10, qs11, qs12, qs13)

        res = []
        for i in files:
            if i not in res:
                res.append(i)

        # word variable will be shown in html when user click on search button
        word = "Searched Result :"
        print("Result")

        print(res)
        files = res

        page = request.GET.get('page', 1)
        paginator = Paginator(files, 10)
        try:
            files = paginator.page(page)
        except PageNotAnInteger:
            files = paginator.page(1)
        except EmptyPage:
            files = paginator.page(paginator.num_pages)

        if files:
            return render(request, 'dashboard/result.html', {'files': files, 'word': word})
        return render(request, 'dashboard/result.html', {'files': files, 'word': word})
