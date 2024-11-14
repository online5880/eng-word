import os
import librosa
import numpy as np
from scipy.spatial.distance import cosine
from django.shortcuts import render
from django.http import JsonResponse
from difflib import SequenceMatcher
from django.conf import settings
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


