import datetime

from django.contrib import admin
from .models import AdvUser, SubCategory, SuperCategory, AdditionalImage, Product, Comment
from .utilites import send_activation_notification
from .forms import SubCategoryForm


def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Письмо с информацией об активации отправлено')
    send_activation_notifications.short_description = 'Отправка писем для активации'


class NonactivatedFilter(admin.SimpleListFilter):
    """Класс для фильтрации пользователей, выполнивших активацию, не выполнивших в течение 3х дней или недели."""
    title = 'Прошли активацию?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return (
            ('activated', 'Прошли'),
            ('threedays', 'Не прошли более 3 дней'),
            ('week', 'Не прошли более недели'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False, date_joined_date_lt=d)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, is_activated=False, date_joined_date_lt=d)


class AdvUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_activated', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (NonactivatedFilter, )
    fields = (
        ('username', 'email'),
        ('first_name', 'last_name'),
        ('send_messages', 'is_active', 'is_activated'),
        ('is_stuff', 'is_superuser'),
        'groups',
        'user_permissions',
        ('last_login', 'date_joined'),
    )
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications, )


class SubCategoryInline(admin.TabularInline):
    model = SubCategory


class SuperCategoryAdmin(admin.ModelAdmin):
    exclude = ('super_category',)
    inlines = (SubCategoryInline,)


class SubCategoryAdmin(admin.ModelAdmin):
    form = SubCategoryForm


class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage


class ProductAdmin(admin.ModelAdmin):
    list_display = ('category', 'title', 'content', 'manufacturer', 'seller', 'created_at')
    fields = (
        'category', 'manufacturer', 'title', 'content', 'price', 'image', 'is_active', 'seller'
    )
    inlines = (AdditionalImageInline,)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # model = Comment
    pass


# class CommentAdmin(admin.ModelAdmin):
#     model = Comment

admin.site.register(AdvUser, AdvUserAdmin)
admin.site.register(SuperCategory, SuperCategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Product, ProductAdmin)
# admin.site.register(Comment, CommentAdmin)

