from typing import Dict
from bs4 import BeautifulSoup
import pandas as pd
import os

class MixlabSoup:
    def __init__(self) -> None:
        self.soup = BeautifulSoup()
        self.pd = pd 
        pass

    def read_html(self, html):
        pass

    def dataframe_timestamp(self, data: Dict[str, str]) -> pd.DataFrame:
        pass

    def meta_realops(self, html:str) -> Dict[str, str]:
        pass

    def floofy_intake(self, html:str) -> Dict[str, str]:
        pass

if __name__ == '__main__':
    pass

