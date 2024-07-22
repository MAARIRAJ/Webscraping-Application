# scraper/admin.py


from django.contrib import admin
from .models import ScrapedData

@admin.register(ScrapedData)
class ScrapedDataAdmin(admin.ModelAdmin):
    list_display = ('url', 'title', 'created_at')
    search_fields = ('url', 'title')
    list_filter = ('created_at',)
