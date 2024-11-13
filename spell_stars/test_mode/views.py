import json
import os
import random
import re
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
import warnings


def test_mode_view(request):
    
    return JsonResponse({"error": "No audio file received"}, status=400)
