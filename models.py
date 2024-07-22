# scraper/models.py

from django.db import models

class ScrapedData(models.Model):
    url = models.URLField(max_length=200)
    title = models.CharField(max_length=255, blank=True, null=True)
    headings = models.TextField(blank=True, null=True)
    paragraphs = models.TextField(blank=True, null=True)
    links = models.TextField(blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or "No Title"


