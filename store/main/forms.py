from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .apps import user_registered
from .models import AdvUser, SuperCategory, SubCategory, Product, AdditionalImage, Comment


class ChangeInfoUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'send_messages')


class RegisterUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    password1 = forms.CharField(
        label='Пароль', widget=forms.PasswordInput, help_text=password_validation.password_validators_help_text_html()
    )
    password2 = forms.CharField(
        label='Пароль(повторно)', widget=forms.PasswordInput, help_text='Пожалуйста, введите пароль еще раз'
    )

    def clean_password(self):
        """Проверка правильности ввода первого пароля"""
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        """Проверка совпадения двух паролей"""
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Пароли не совпадают', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        """Сохранение нового пользователя"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registered.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'send_messages')


class SubCategoryForm(forms.ModelForm):
    super_category = forms.ModelChoiceField(
        queryset=SuperCategory.objects.all(), empty_label=None, label='Надкатегория', required=True
    )

    class Meta:
        model = SubCategory
        fields = '__all__'


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label='')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {'seller': forms.HiddenInput}


class UserCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = {'is_active',}
        widgets = {'product': forms.HiddenInput}


class GuestCommentForm(forms.ModelForm):
    captcha = CaptchaField(label='Введите текст с изображения', error_messages={'invalid': 'Неправильный текст'})

    class Meta:
        model = Comment
        exclude = {'is_active',}
        widgets = {'product': forms.HiddenInput}


AIFormSet = inlineformset_factory(Product, AdditionalImage, fields='__all__')
