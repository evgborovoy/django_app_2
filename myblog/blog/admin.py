from django.contrib import admin

from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "author", "publish", "status"]  # Отображаемые поля
    list_filter = ["status", "created", "publish", "author"]  # Добавление фильтрации
    search_fields = ["title", "body"]  # Строка поиска (искать по полям)
    prepopulated_fields = {"slug": ("title",)}  # Автоматическое заполнение поля slug
    raw_id_fields = ["author"]  # Теперь поле не выпадающим списком, а простым вводом
    date_hierarchy = "publish"  # Навигационные ссылки
    ordering = ["status", "publish"]  # Сортировка по умолчанию
