"""
        Requirements:
        NLTK:
           nltk.download('stopwords')
           nltk.download('punkt')
"""

import json

import nltk

nltk.download("stopwords")
nltk.download("punkt")

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from difflib import SequenceMatcher

from utils.jsonLoader import read_json


class Classifier:
    def __init__(self):
        """
            Init method for class
        """
        self.stopwords = set(stopwords.words("english"))
        self.data = []

    def start(self):
        """
          Read JSON file and assign it to a variable for easy parsing.
        """
        self.data = read_json("database")

    def classify(self, query: str = None):
        """
          Generate a response, if no response 'None' wil be returned.
          Method takes an input that is a string.
        """
        # Prepare query for keyword matching
        if query == None:
            return None
        # Tokenize words i.e. ['the', 'blue', 'cat']
        tokens = word_tokenize(query)

        # Remove 'Stop Words' i.e. ['the', 'blue', 'cat'] -> ['blue', 'cat']
        fi = []
        for w in tokens:
            if w not in self.stopwords:
                fi.append(w)

        fi = " ".join(fi)
        # Search JSON file for matching keywords
        for x in range(len(self.data["data"])):
            for i in range(len(self.data["data"][x]["keywords"])):
                # Get simlarity score. i.e. "blue cat", "fat blue cat" ~= 75%
                r = SequenceMatcher(a=fi, b=self.data["data"][x]["keywords"][i]).ratio()
                if r > 0.75:
                    # If simaliratiy above 75% return the result, and break the iteration.
                    return self.data["data"][x]["response"]
