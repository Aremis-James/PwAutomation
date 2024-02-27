import site
import sys
import os
import asyncio
import re
import time
from pprint import pprint
from datetime import datetime
from typing import Literal
from pydantic import BaseModel
from playwright.async_api import async_playwright, expect, TimeoutError

parent_dir = os.path.dirname(os.path.dirname(__file__))

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from config import settings


LOGIN = settings.login_config
FLOOFY = settings.floofy_config
META = settings.meta_config

class LabSelection(BaseModel):
    """Represents the selection of a lab with a specified location."""
    lab : Literal['NY', 'LA', 'FL']



class SiteAutomation:
    """
    Automates site interaction tasks such as login, navigation, and screenshot capture.
    Designed to work with headless browsers using the Playwright library.
    """
    def __init__(self, headless: bool, credentials: settings.UserCredentialsConfig, login_url:str) -> None:
        self.headless = headless
        self.login_url = login_url
        self.browser = None
        self.context = None
        self.page = None
        self.__default_path = os.path.join(os.environ['USERPROFILE'], 'Downloads') if os.name == 'nt' else os.path.join(
        os.path.expanduser('~'), 'Downloads')
        self.__default_folder = None
        self.credentials = credentials


    async def floofy(self, navigate_to:str, lab:LabSelection,):
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=self.headless)
            if os.path.exists('../automation/mixlabstate.json'):
                    self.context = await self.browser.new_context(storage_state='mixlabstate.json')
                    await self.context.tracing.start(screenshots=True, snapshots=True)
                    self.page = await self.context.new_page()
            else:
                self.context = await self.browser.new_context()
                self.page = await self.context.new_page()
                await self.login(login_url=self.login_url, username=self.credentials.email, password=self.credentials.password)
                await expect(self.page.locator('id=LOGGED_IN_BAR')).to_be_visible()
                await self.context.storage_state(path=f'{(await self.page.title()).lower()}state.json')
            try:
                await self.navigate(navigate_to)
                await asyncio.sleep(5)
                screenshot_path = os.path.join(self.__default_path, f'{lab}floofy.png')
                await self.page.screenshot(full_page=True, path=screenshot_path)
            except TimeoutError as e:
                asyncio.sleep(5)
                await self.context.tracing.stop(path='trace.zip')
            finally:
                await self.close_browser()


    async def meta(self, navigate_to:str):
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()

            await self.login(login_url=self.login_url, username=self.credentials.email, password=self.credentials.password )
            await expect(self.page).to_have_title('Login · Metabase')
            await self.navigate(navigate_to, sleep=2)
            await self.screenshot(f'meta.png')
            await self.close_browser()


    async def __is_logged_in(self):
        """Checks if the user is logged in based on session cookies."""
        cookies = await self.page.context.cookies()
        # Look for a specific cookie known to be set after login, e.g., a session cookie
        for cookie in cookies:
            if cookie['name'] == 'session_id':  # Example cookie name
                return True
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

 

# async def main():
#         s = time.perf_counter()

#         mixlab_meta = SiteAutomation(headless=False, credentials=LOGIN, login_url= META['base'])
#         mixlab_floofy = SiteAutomation(headless=False, credentials=LOGIN, login_url= FLOOFY['base'])

#         task = [
#             mixlab_floofy.floofy(FLOOFY['intake_ny'], lab='NY'),
#             mixlab_meta.meta(META['allpharm'])
#         ]

#         await asyncio.gather(*task)

#         elapsed = time.perf_counter() - s
#         print(f'{__file__} excute in {elapsed:0.2f} seconds')

if __name__ == '__main__':
    site = SiteAutomation(headless=False,credentials=LOGIN, login_url=FLOOFY.base)
    asyncio.run(site.floofy(FLOOFY.intake_fl, lab='FL'))
    asyncio.run(site.floofy(FLOOFY.intake_ny, lab='NY'))
    
