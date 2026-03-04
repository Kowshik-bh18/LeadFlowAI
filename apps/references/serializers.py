from rest_framework import serializers
from .models import ReferenceDocument, DocumentChunk


class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ['id', 'chunk_index', 'text', 'token_count']


class ReferenceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceDocument
        fields = [
            'id', 'title', 'description', 'doc_type',
            'status', 'total_chunks', 'created_at', 'updated_at',
        ]
