from django.db import models
from django.conf import settings
from pgvector.django import VectorField
import uuid


class ReferenceDocument(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('indexed', 'Indexed'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='references/', blank=True, null=True)
    raw_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    doc_type = models.CharField(max_length=100, blank=True, help_text='e.g. Security Policy, Data Retention')
    total_chunks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reference Document'

    def __str__(self):
        return self.title


class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(ReferenceDocument, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.PositiveIntegerField(default=0)
    text = models.TextField()
    embedding = VectorField(dimensions=3072, null=True, blank=True)  # text-embedding-3-small dim
    token_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]

    def __str__(self):
        return f"{self.document.title} – chunk {self.chunk_index}"
