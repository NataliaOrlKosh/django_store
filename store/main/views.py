from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.core.signing import BadSignature
from django.db.models import Q
from django.db.models.signals import post_save
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView

from .forms import ChangeInfoUserForm, RegisterUserForm, SearchForm, ProductForm, AIFormSet, UserCommentForm, \
    GuestCommentForm
from .models import AdvUser, SubCategory, Product, Comment
from .utilites import signer, send_new_comment_notification


def index(request):
    products = Product.objects.filter(is_active=True)[:20]
    context = {
        'products': products,
    }
    return render(request, 'main/index.html', context)


def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


@login_required
def profile(request):
    products = Product.objects.filter(seller=request.user.pk)
    context = {
        'products': products
    }
    return render(request, 'main/profile.html', context)


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class StoreLoginView(LoginView):
    template_name = 'main/login.html'


class StoreLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


class ChangeInfoUserFormView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeInfoUserForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Данные пользователя успешно изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class UserPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Ваш пароль изменен'


class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


def by_category(request, pk):
    category = get_object_or_404(SubCategory, pk=pk)
    products = Product.objects.filter(is_active=True, category=pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        products = products.filter(q)
    else:
        keyword = ''
        form = SearchForm(initial={'keyword': keyword})
        paginator = Paginator(products, 2)
        if 'page' in request.GET:
            page_num = request.GET['page']
        else:
            page_num = 1
        page = paginator.get_page(page_num)
        context = {
            'category': category,
            'page': page,
            'products': page.object_list,
            'form': form
        }
        return render(request, 'main/by_category.html', context)


def detail(request, category_pk, pk):
    product = get_object_or_404(Product, pk=pk)
    ais = product.additionalimage_set.all()
    comments = Comment.objects.filter(product=pk, is_active=True)
    initial = {'product': product.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = GuestCommentForm
    form = form_class(initial=initial)
    if request.method == 'POST':
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
    context = {
        'product': product,
        'ais': ais,
        'comments': comments,
        'form': form
    }
    return render(request, 'main/detail.html', context)


@login_required
def profile_product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    ais = product.additionalimage_set.all()
    context = {
        'product': product,
        'ais': ais,
    }
    return render(request, 'main/profile_product_detail.html', context)


@login_required
def profile_product_add(request):
    """Контроллер для добавления товара"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=product)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Товар добавлен')
                return redirect('main:profile')
    else:
        form = ProductForm(initial={'seller': request.user.pk})
        formset = AIFormSet()
    context = {
        'form': form,
        'formset': formset
    }
    return render(request, 'main/profile_product_add.html', context)


@login_required
def profile_product_change(request, pk):
    """Контроллер для изменения товара"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=product)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Информация о товаре изменена')
                return redirect('main:profile')
    else:
        form = ProductForm(instance=product)
        formset = AIFormSet(instance=product)
    context = {
        'form': form,
        'formset': formset
    }
    return render(request, 'main/profile_product_change.html', context)


@login_required
def profile_product_delete(request, pk):
    """Контроллер для удаления товара"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.add_message(request, messages.SUCCESS, 'Информация о товаре удалена')
        return redirect('main:profile')
    else:
        context = {
            'product': product
        }
        return render(request, 'main/profile_product_delete.html', context)


def post_save_dispatcher(sender, **kwargs):
    author = kwargs['instance'].product.seller
    if kwargs['created'] and author.send_messages:
        send_new_comment_notification(kwargs['instance'])


post_save.connect(post_save_dispatcher, sender=Comment)
