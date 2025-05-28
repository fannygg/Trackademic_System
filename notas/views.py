from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .mongo import get_collection

class GradesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = request.user.profile.codigo
        grades = list(get_collection('grades').find({'student_id': student_id}, {'_id': 0}))
        return Response(grades)
