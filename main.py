import toml
import asyncio
import logging
import os
import time
import schedule
import keyring as kr
from dotenv import load_dotenv
from communication.slackbot import SlackComs 
from config.settings import UserCredentialsConfig,  MetaPagesConfig, FloofyPagesConfig, EMAIL
from site_automation.navigation import FloofyAutomation, MetaAutomation


load_dotenv()

logging.basicConfig(filename='automation_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


PASSWORD = kr.get_password(service_name=os.getenv('SERVICE_ID'),username=EMAIL)
LOGIN = UserCredentialsConfig(email=EMAIL, password=PASSWORD)
META = MetaPagesConfig()
FLOOFY = FloofyPagesConfig()
SLACK_TOKEN = os.getenv('SLACK_TOKEN')

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
            results = await asyncio.gather(*task)
            logging.info("All tasks completed successfully.")
        except Exception as e:
            logging.error(f'Exception occurred: {e}', exc_info=True)

        elapsed = time.perf_counter() - s
        logging.info(f'{__file__} excute in {elapsed:0.2f} seconds')
        return results

 
def run_tasks():
     asyncio.run(main())

if __name__ == '__main__':
    slack = SlackComs(token=SLACK_TOKEN, channel=os.getenv('SLACK_CHANNEL_ID'))
    results = asyncio.run(main())
    if results:
        la, ny, meta = results
    for index in range(len(results)):
        slack.upload(results[index][1], 'Test_Screenshot', 'Test')


    # weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    # for day in weekdays:
    #     for hour in range(8, 20):  # From 8 AM to 7PM
    #         schedule.every().__getattribute__(day).at(f'{hour:02d}:00').do(run_tasks)

    # # Schedule tasks for Saturday
    # for hour in range(8, 17):  # From 8 AM to 4 PM
    #     schedule.every().saturday.at(f"{hour:02d}:00").do(run_tasks)
    # schedule.every().saturday.at("16:30").do(run_tasks)

    # logging.info("Scheduler started. Waiting for tasks to run.")
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1300) # check every hour~