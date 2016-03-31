from django.shortcuts import render
from rest_framework import generics
from skill_match.models import HendersonPark
from skill_match.serializers import HendersonParkSerializer


class ListHendersonParks(generics.ListAPIView):
    queryset = HendersonPark.objects.all()
    serializer_class = HendersonParkSerializer
