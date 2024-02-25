import sys
import os

parent_dir = os.path.dirname(os.path.dirname(__file__))

if parent_dir not in sys.path:
    sys.path.append(parent_dir)


import asyncio
import json
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
    Typed dictionary to represent user credentials.

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
    def __init__(self, headless: bool, credentials: Credentials, default_url: str) -> None:
        self.default_url = default_url
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        pass


    def launch_browser(self):
        pass

    def __save_storage_state(self):
        pass
    
    def __load_storage_state(self):
        pass

    def __del_storage_state(self):
        if os.path.exists('state.json'):
            with open('state.json', 'r') as file:
                cookies = json.load(file)
                try:
                    expiry = datetime.utcfromtimestamp(int(cookies['origins'][0]['localStorage'][0]['value']))
                    if datetime.utcnow() >= expiry:
                        os.remove('state.json')
                except (IndexError, KeyError, ValueError) as e:
                            os.remove('state.json')

        pass

    def __validate_login(self, credentials):  
        pass

    def login(self):
        pass

    def screenshot(self):
        pass


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # if os.path.exists('state.json'):
        #     context = await browser.new_context(storage_state='state.json')
        #     page = await context.new_page()
        # else:
        #     context = await browser.new_context()
        #     page = await context.new_page()


        await page.goto(FLOOFY['base'])
        await page.get_by_label('email').fill(LOGIN.email)
        await page.get_by_label('password').fill(LOGIN.password)
        await expect(page.get_by_label('email')).to_have_value(LOGIN.email)
        await expect(page.get_by_label('password')).to_have_value(LOGIN.password)
        await page.get_by_role('button', name='Log in').click()

        await expect(page.locator('id=LOGGED_IN_BAR')).to_be_visible()
        await context.storage_state(path='state.json')
        await page.goto(FLOOFY['intake'])

        await page.locator('//*[@id="root"]/div/div[2]/div/div/div[2]/div[1]/div/div[2]/div/div/div[2]/label/span/span').click()

        # await asyncio.sleep(5)
        await page.screenshot(full_page=True, path='test.png')
        await context.close()
        await browser.close()

        

if __name__ == '__main__':
    import time
    s = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - s
    print(f'{__file__} excute in {elapsed:0.2f} seconds')
    os.remove('test.png')
    os.remove('state.json')
