import os
import toml
import keyring as kr
from functools import wraps
from dotenv import load_dotenv


def __load_env_variables(func):
    @wraps(func)  
    def wrapper(*args, **kwargs):
        load_dotenv()
        return func(*args, **kwargs)
    return wrapper


@__load_env_variables
def login_config():
    service_id = os.getenv('SERVICE_ID')
    account_id = os.getenv('EMAIL')

    with open('./config/settings.toml', 'r') as config_toml:
        user_config = toml.load(config_toml)['login']
        user_config['account_id'] = account_id
        user_config['account_key'] = kr.get_password(service_name=service_id, username=account_id)
    return user_config


@__load_env_variables
def floofy_config():
    with open('./config/settings.toml', 'r') as config_toml:
        nav_config = toml.load(config_toml)['floofy_pages']
        nav_config['base'] = os.getenv('FLOOFY', nav_config['base'])
        nav_config['intake'] = os.getenv("INTAKE", nav_config['intake'])
    return nav_config


@__load_env_variables
def navigate_config():
    with open('./config/settings.toml', 'r') as config_toml:
        nav_config = toml.load(config_toml)['meta_pages']
        nav_config['base'] = os.getenv('META', nav_config['base'])
        nav_config['allpharm'] = os.getenv('ALLPHARM', nav_config['allpharm'])
        nav_config['realtime'] = os.getenv('REALTIME', nav_config['realtime'])
        nav_config['vet_orders'] = os.getenv('VET_ORDERS', nav_config['vet_orders'])
    return nav_config


@__load_env_variables
def slack_config():
    with open('./config/settings.toml', 'r') as config_toml:
        coms_config = toml.load(config_toml)['slack']
        coms_config['channel_id'] = os.getenv('CHANNEL_ID', coms_config['channel_id'])
        coms_config['token'] = os.getenv('SLACK_TOKEN', coms_config['token'])
    return coms_config


if __name__ == '__main__':
    pass