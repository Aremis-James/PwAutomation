import toml
import asyncio
import os
import time
import schedule
import keyring as kr
from dotenv import load_dotenv
from config.settings import UserCredentialsConfig,  MetaPagesConfig, FloofyPagesConfig, EMAIL
from site_automation.navigation import FloofyAutomation, MetaAutomation


load_dotenv()

PASSWORD = kr.get_password(service_name=os.getenv('SERVICE_ID'),username=EMAIL)
LOGIN = UserCredentialsConfig(email=EMAIL, password=PASSWORD)
META = MetaPagesConfig()
FLOOFY = FloofyPagesConfig()

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
        try:
            await asyncio.gather(*task)
        except Exception as e:
             print(f'{e}')

        elapsed = time.perf_counter() - s
        print(f'{__file__} excute in {elapsed:0.2f} seconds')

 


if __name__ == '__main__':
    asyncio.run(main())