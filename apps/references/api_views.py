from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ReferenceDocument
from .serializers import ReferenceDocumentSerializer


class DocumentListAPIView(generics.ListAPIView):
    serializer_class = ReferenceDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReferenceDocument.objects.filter(user=self.request.user)


class DocumentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            doc = ReferenceDocument.objects.get(pk=pk, user=request.user)
        except ReferenceDocument.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        return Response({
            'id': str(doc.id),
            'status': doc.status,
            'total_chunks': doc.total_chunks,
        })
