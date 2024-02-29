import pickle
import site
import sys
import os
import asyncio
import re
import time
from datetime import datetime
from typing import Literal
import playwright
from pydantic import BaseModel
from playwright.async_api import async_playwright, expect, TimeoutError, StorageState
from cryptography.fernet import Fernet
from functools import wraps
import tracemalloc

parent_dir = os.path.dirname(os.path.dirname(__file__))

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from config import settings


LOGIN = settings.login_config
FLOOFY = settings.floofy_config
META = settings.meta_config
KEY_ = settings.KEY

class LabSelection(BaseModel):
    """Represents the selection of a lab with a specified location."""
    lab : Literal['NY', 'LA', 'FL']



def timer(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter() - start
        print(f"Execution time of {func.__name__}: {end:0.5f} seconds")
        return result
    return wrapper

class SiteAutomation:
    """
    Automates site interaction tasks such as login, navigation, and screenshot capture.
    Designed to work with headless browsers using the Playwright library.
    """
    def __init__(self, headless: bool, credentials: settings.UserCredentialsConfig) -> None:
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.__default_path = os.path.join(os.environ['USERPROFILE'], 'Downloads') if os.name == 'nt' else os.path.join(
        os.path.expanduser('~'), 'Downloads')
        self.__default_folder = 'Queue'
        self.folder_path = os.path.join(self.__default_path, self.__default_folder)
        self.credentials = credentials



    async def launch_context(self, storage:str=None):
            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=self.headless)
                if storage:
                    self.context = await self.browser.new_context(storage_state=storage)
                else:
                    self.context = await self.browser.new_context()
                return self.context



    async def screenshot(self, prefix:str='meta', sleep: int|None=None):
         
            if sleep:
                await asyncio.sleep(sleep)

            screenshot_path = os.path.join(self.folder_path, f'{prefix}mixlab{datetime.now().strftime("%m%d%y_%I%M")}.png')
            await self.page.screenshot(full_page=True, path=screenshot_path)



    async def __is_logged_in(self):
        """Checks if the user is logged in based on session cookies."""
        cookies = await self.page.context.cookies()
        # Look for a specific cookie known to be set after login, e.g., a session cookie
        if len(cookies) != 0:
                return True
        else:
            return False


    async def navigate(self, page:str , sleep:int|None=None):
        """Navigates to a specified page, optionally waiting for a given time."""
        if sleep:
            await asyncio.sleep(sleep)
        await self.page.goto(page)

        
    async def login(self, username:str, password: str, login_url:str):# loaded:str|None = None):
        """Performs login action on the site."""
        await self.page.goto(url=login_url)
        await self.page.get_by_label(re.compile('(email|username)', re.IGNORECASE)).fill(username)
        await self.page.get_by_label('password').fill(password)
        await expect(self.page.get_by_label(re.compile('(email|username)', re.IGNORECASE))).to_have_value(username)
        await expect(self.page.get_by_label('password')).to_have_value(password)
        await self.page.get_by_role('button', name=re.compile('(sign in|log in)', re.IGNORECASE)).click()
           
    
    
    async def close_browser(self):
        """Closes the browser and all associated contexts."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    def save_storage(self, state: StorageState):
        cipher = Fernet(KEY_)
        with open('../automation/encrypted_data.bin', 'wb') as file:
                    file.write(cipher.encrypt(pickle.dumps(state)))


    def load_storage(self):
        cipher = Fernet(KEY_)
        if os.path.exists('../automation/encrypted_data.bin'):
                    with open('../automation/encrypted_data.bin', 'rb') as file:
                        storage = pickle.loads(cipher.decrypt(file.read()))
        return storage



class MetaAutomation(SiteAutomation):
    def __init__(self, headless: bool, credentials: settings.UserCredentialsConfig) -> None:
        super().__init__(headless, credentials)


    # @timer
    async def main(self, start_url:str, navigate_to:str):
           async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=self.headless)
                self.context = await self.browser.new_context()
                self.page = await self.context.new_page()

                await self.login(login_url=start_url, username=self.credentials.email, password=self.credentials.password )
                await expect(self.page).to_have_title('Login · Metabase')
                await self.navigate(navigate_to, sleep=2)
                await self.screenshot(sleep=7)
                await self.close_browser()



class FloofyAutomation(SiteAutomation):
    def __init__(self, headless: bool, credentials: settings.UserCredentialsConfig) -> None:
        super().__init__(headless, credentials)


    # @timer
    async def main(self, start_url:str, navigate_to:str, prefix:LabSelection):
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=self.headless)
            if self.load_storage():
                    self.context = await self.browser.new_context(storage_state=self.load_storage())
                    await self.context.tracing.start(screenshots=True, snapshots=True)
                    self.page = await self.context.new_page()
            else:
                self.context = await self.browser.new_context()
                self.page = await self.context.new_page()
                await self.login(login_url=start_url, username=self.credentials.email, password=self.credentials.password)
                await expect(self.page.locator('id=LOGGED_IN_BAR')).to_be_visible()
                self.save_storage(await self.context.storage_state())

            try:
                await self.navigate(navigate_to)
                await self.screenshot(prefix=prefix, sleep=5)
            except TimeoutError as e:
                await self.context.tracing.stop(path='trace.zip')
            finally:
                await self.close_browser()
        

 



if __name__ == '__main__':
    # LA = FloofyAutomation(headless=False, credentials=LOGIN)
    # asyncio.run(LA.main(FLOOFY.base,FLOOFY.intake_la,prefix='LA'))
    async def main():
        s = time.perf_counter()

        LA = FloofyAutomation(headless=False, credentials=LOGIN)
        NY = FloofyAutomation(headless=False, credentials=LOGIN)
        meta = MetaAutomation(headless=False, credentials=LOGIN)

        task = [
            LA.main(FLOOFY.base,FLOOFY.intake_la,'LA'),
            NY.main(FLOOFY.base,FLOOFY.intake_ny,'NY'),
            meta.main(META.base,META.allpharm)
        ]

        await asyncio.gather(*task)

        elapsed = time.perf_counter() - s
        print(f'{__file__} excute in {elapsed:0.2f} seconds')

    asyncio.run(main())

  
    
