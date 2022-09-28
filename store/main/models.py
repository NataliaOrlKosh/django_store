from django.contrib.auth.models import AbstractUser
from django.db import models

from .utilites import get_timestamp_path


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Вы зарегистрированы?')
    send_messages = models.BooleanField(
        default=True, verbose_name='Вы хотите получать оповещения о комментариях для ваших товаров?'
    )

    def delete(self, *args, **kwargs):
        for product in self.product_set.all():
            product.delete()
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass


class Category(models.Model):
    """Базовая модель категорий товаров"""
    name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name='Название')
    order = models.SmallIntegerField(default=0, db_index=True, unique=True, verbose_name='Порядок')
    super_category = models.ForeignKey(
        'SuperCategory', on_delete=models.PROTECT, null=True,
        blank=True, verbose_name='Категория товаров'
    )


class SuperCategoryManager(models.Manager):
    """Диспетчер записей для выбора надкатегорий"""
    def get_queryset(self):
        return super().get_queryset().filter(super_category__isnull=True)


class SuperCategory(Category):
    """"Модель надкатегорий"""
    objects = SuperCategoryManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'Категория товаров'
        verbose_name_plural = 'Категории товаров'


class SubCategoryManager(models.Manager):
    """Диспетчер записей для выбора подкатегорий"""
    def get_queryset(self):
        return super().get_queryset().filter(super_category__isnull=False)


class SubCategory(Category):
    """"Модель подкатегорий"""
    objects = SubCategoryManager()

    def __str__(self):
        return f'{self.super_category.name} - {self.name}'

    class Meta:
        proxy = True
        ordering = ('super_category__order', 'super_category__name', 'order', 'name')
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'


class Product(models.Model):
    category = models.ForeignKey(SubCategory, on_delete=models.PROTECT, verbose_name='Категория')
    title = models.CharField(max_length=40, verbose_name='Название товара')
    content = models.TextField(verbose_name='Описание товара')
    price = models.FloatField(default=0, verbose_name='Цена')
    manufacturer = models.CharField(max_length=50, verbose_name='Производитель')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Изображение')
    seller = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Продавец')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Наличие товара')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Добавлено')

    def delete(self, *args, **kwargs):
        for image in self.additionalimage_set.all():
            image.delete()
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class AdditionalImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Изображение')

    class Meta:
        verbose_name = 'Дополнительное изображение'
        verbose_name_plural = 'Дополнительные изображения'


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    author = models.CharField(max_length=40, verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Виден всем')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Добавлено')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
