from importlib.metadata import files
import sys
import os
from time import sleep

parent_dir = os.path.dirname(os.path.dirname(__file__))

if parent_dir not in sys.path:
    sys.path.append(parent_dir)


import asyncio
import glob
import re
from datetime import datetime
from typing import Literal, TypedDict
from pydantic import BaseModel, EmailStr, ValidationError
from playwright.async_api import async_playwright, expect
from config import settings


class Login(BaseModel):
    """
    Represents user login credentials with email and password.

    Validates the email format using Pydantic's EmailStr.

    Attributes:
        email (EmailStr): Valid email address.
        password (str): User's password.
    """
    email: EmailStr
    password: str

class Credentials(TypedDict):
    """
    This class is used to define the structure of a dictionary holding user credentials,
    specifically containing 'email' and 'password' fields.

    Attributes:
        email (str): The email address of the user.
        password (str): The password for the user's account.
        """
    email: str
    password: str

LOGIN = Login(email= settings.login_config()['account_id'],
              password=settings.login_config()['account_key'])


FLOOFY = settings.floofy_config()


Labs = Literal['NY', 'LA', 'FL']

class LabSelection(BaseModel):
    lab : Labs



class SiteAutomation:
    def __init__(self, headless: bool, credentials: Credentials, login_url:str, lab:LabSelection) -> None:
        self.headless = headless
        self.login_url = login_url
        self.site = lab if lab else 'meta'
        self.browser = None
        self.context = None
        self.page = None
        self.credentials = credentials
        self.__storage_name = ''


    async def main(self):
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=self.headless)
            if os.path.exists(self.__storage_name):
                self.context = await self.browser.new_context(storage_state=self.__storage_name)
                self. page = await self.context.new_page()
                await self.navigate(FLOOFY['intake'])
                await self.page.locator('//*[@id="root"]/div/div[2]/div/div/div[2]/div[1]/div/div[2]/div/div/div[2]/label/span/span').click()
                await self.screenshot(file_path='test.png')
                await self.close_browser()
            else:
                self.context = await self.browser.new_context()

                self. page = await self.context.new_page()

                await self.login(username=self.credentials.email,password=self.credentials.password)
                await self.__validate_login() # find a more efficient way later
                self.__storage_name = self.__generate_storage_filename(identifier=await self.page.title())
                await self.__save_storage_state()


                await self.navigate(FLOOFY['intake'])
                
                await self.page.locator('//*[@id="root"]/div/div[2]/div/div/div[2]/div[1]/div/div[2]/div/div/div[2]/label/span/span').click()
                text = await self.page.get_by_role('value', name='1').text_content()
                print(text)
                
                await self.screenshot(file_path='test.png')
                await self.close_browser()

    

    async def __save_storage_state(self):
        if self.__storage_name:
            await self.context.storage_state(path=self.__storage_name)


    async def navigate(self, page ):
        await self.page.goto(page)


    

    
    async def login(self, username:str, password: str):# loaded:str|None = None):
        
        await self.page.goto(url=self.login_url)

        await self.page.get_by_label(re.compile('(email|username)', re.IGNORECASE)).fill(username)
        await self.page.get_by_label('password').fill(password)

        await expect(self.page.get_by_label(re.compile('(email|username)', re.IGNORECASE))).to_have_value(username)
        await expect(self.page.get_by_label('password')).to_have_value(password)

        await self.page.get_by_role('button', name=re.compile('(submit|log in)', re.IGNORECASE)).click()
           

    
    async def __validate_login(self): 
        await expect(self.page.locator('id=LOGGED_IN_BAR')).to_be_visible() 


    async def screenshot(self, file_path,):
        await asyncio.sleep(5)
        await self.page.screenshot(timeout=50000, full_page=True, path=file_path)
        
        

    async def __save_storage_state(self):
        if self.__storage_name:
            await self.context.storage_state(path=self.__storage_name)
    
 


    async def close_browser(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    def __generate_storage_filename(self, identifier: str = None) -> str:
            base_name = identifier if identifier else "storage_state"
            timestamp = datetime.now().strftime('%Y%m%d')
            return f"{base_name}_{timestamp}.json"
    
    def __del_storage_state(self):
        if os.path.exists(self.__storage_name):
            os.remove(self.__storage_name)


if __name__ == '__main__':
    import time
    s = time.perf_counter()
    site = SiteAutomation(headless=False, credentials=LOGIN, login_url= FLOOFY['base'], lab='NY')
    asyncio.run(site.main())
    elapsed = time.perf_counter() - s
    print(f'{__file__} excute in {elapsed:0.2f} seconds')
    
