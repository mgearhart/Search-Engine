# Class that is inherited from fastapi
from fastapi import FastAPI # pip install fastapi
import json

class SearchEngineAPI(FastAPI):
    '''
    Class that holds the summary files and inherits from FastAPI
    '''
    def __init__(self):
        self.SUMMARY1 = {}
        self.SUMMARY2 = {}
        self.SUMMARY3 = {}
        self.SUMMARY4 = {}

        with open("../databases/cleaned_id_to_summary_part1.json", "r") as f:
            self.SUMMARY1 = json.load(f)
        with open("../databases/cleaned_id_to_summary_part2.json", "r") as f:
            self.SUMMARY2 = json.load(f)
        with open("../databases/cleaned_id_to_summary_part3.json", "r") as f:
            self.SUMMARY3 = json.load(f)
        with open("../databases/cleaned_id_to_summary_part4.json", "r") as f:
            self.SUMMARY4 = json.load(f)

        super().__init__()