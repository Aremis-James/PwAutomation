import pickle
import sys
import os
import asyncio
import re
import time
from datetime import datetime
from typing import Literal
from pydantic import BaseModel
from playwright.async_api import async_playwright, expect, TimeoutError, StorageState
from cryptography.fernet import Fernet
from functools import wraps

parent_dir = os.path.dirname(os.path.dirname(__file__))

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from config import settings
import logging

# Configure logging
logging.basicConfig(filename='automation_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')



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
        logging.info(f"Execution time of {func.__name__}: {end:0.5f} seconds")
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



    async def screenshot(self, prefix:str='meta', sleep: int|None=None):
         
            if sleep:
                await asyncio.sleep(sleep)
            screenshot_path = os.path.join(self.folder_path, f'{prefix}mixlab{datetime.now().strftime("%m%d%y_%I%M")}.png')
            await self.page.screenshot(full_page=True, path=screenshot_path)
            logging.info('Screen Shot Saved!')



    async def __is_logged_in(self):
        """Checks if the user is logged in based on session cookies."""
        cookies = await self.page.context.cookies()
        return len(cookies) != 0


    async def navigate(self, page:str , sleep:int|None=None):
        """Navigates to a specified page, optionally waiting for a given time."""
        if sleep:
            await asyncio.sleep(sleep)
        await self.page.goto(page)

        
    async def login(self, username:str, password: str, login_url:str):
        """Performs login action on the site."""
        email_or_username = re.compile('(email|username)', re.IGNORECASE)
        await self.page.goto(url=login_url)
        await self.page.get_by_label(email_or_username).fill(username)
        await self.page.get_by_label('password').fill(password)
        await expect(self.page.get_by_label(email_or_username)).to_have_value(username)
        await expect(self.page.get_by_label('password')).to_have_value(password)
        await self.page.get_by_role('button', name=re.compile('(sign in|log in)', re.IGNORECASE)).click()
           
    
    async def close_browser(self):
        """Closes the browser and all associated contexts."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()


    def save_storage(self, prefix: str, state: StorageState):
        cipher = Fernet(KEY_)
        with open(f'../automation/encrypted_{prefix}data.bin', 'wb') as file:
                    file.write(cipher.encrypt(pickle.dumps(state)))
                    logging.info(f'Storage State saved , pickled, & encrypted')


    def load_storage(self, prefix: str):
        cipher = Fernet(KEY_)
        storage_path = f'../automation/encrypted_{prefix}data.bin'
        if os.path.exists(storage_path):
            with open(storage_path, 'rb') as file:
                encrytped_file = file.read()
                try:
                    storage = pickle.loads(cipher.decrypt(encrytped_file))
                    valid_cookie = next(
                         (cookie for cookie in storage['cookies'] if datetime.utcnow() < datetime.utcfromtimestamp(cookie['expires'])),
                         None
                    )
                    if valid_cookie: 
                         return storage 

                    else: 
                         os.remove(storage_path)
                         logging.info("Expired session storage removed.")
                   
                except Exception as e:
                     logging.error(f"Error decrypting or unpickling storage data: {e}")
        else:
             logging.warning(f"Storage file does not exist: {storage_path}")
                             
        return None



class MetaAutomation(SiteAutomation):
    def __init__(self, headless: bool, credentials: settings.UserCredentialsConfig) -> None:
        super().__init__(headless, credentials)

    


    @timer
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

    async def __nonzero_intake(self, selector:str):
        ''' Wait for the element's content to change from 'Intake(0) '''
        await self.page.wait_for_function(f"""
            () => {{
                const el = document.querySelector('{selector}');
                if (!el) return false;
                const text = el.textContent.trim();
                return text !== 'Intake(0)';
            }}
            """)
        return True
         


    @timer
    async def main(self, start_url:str, navigate_to:str, prefix:LabSelection):
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=self.headless)
            storage_state = self.load_storage('floofy')
            if storage_state:
                    self.context = await self.browser.new_context(storage_state=storage_state)
                    await self.context.tracing.start(screenshots=True, snapshots=True)
                    self.page = await self.context.new_page()
            else:
                self.context = await self.browser.new_context()
                self.page = await self.context.new_page()
                await self.login(login_url=start_url, username=self.credentials.email, password=self.credentials.password)
                await expect(self.page.locator('id=LOGGED_IN_BAR')).to_be_visible()
                cookies = await self.context.storage_state()
                self.save_storage('floofy', await self.context.storage_state())

            try:
                await self.navigate(navigate_to)
                selector = 'h2.text-2xl.font-brown-pro.leading-normal.text-gracy-100'
                if await self.__nonzero_intake(selector):
                    await self.screenshot(prefix=prefix, sleep=5)
            except TimeoutError as e:
                logging.error(f'Timeout {e}')
                await self.context.tracing.stop(path='trace.zip')
            finally:
                await self.close_browser()
        
if __name__ == '__main__':
     pass
