import toml
import os
import sys
from dotenv import load_dotenv

from site_automation.site_nav import FLOOFY

parent_dir = os.path.dirname(os.path.dirname(__file__))

if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from config.settings import login_config, floofy_config, meta_config

with open('./config/settings.toml','r') as toml_test:
    config = toml.load(toml_test)

    ###   Test Toml files before updating ###

def test_default_login():
    assert config['login']['account_id'] == 'username'
    assert config['login']['account_key'] == 'password'

def test_default_slack():
    assert config['slack']['channel_id'] == '#####'
    assert config['slack']['token'] == '#######'


def test_default_base_url():
    assert config['meta_pages']['base'] == 'meta_base'
    assert config['floofy_pages']['base'] == 'floofy_base'
   
###### After config ########

def test_login():
    login = login_config()
    assert login['account_id'] == os.getenv('EMAIL')


def test_floofy_pages():
    pages = floofy_config()

    assert pages['base'] == os.getenv('FLOOFY')
    assert pages['intake'] == os.getenv('INTAKE')


def test_meta_pages():
    pages = meta_config()

    assert pages['base'] == os.getenv('META')
    assert pages['allpharm'] == os.getenv('ALLPHARM')


