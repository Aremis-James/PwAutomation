import os
import toml
import keyring as kr
from functools import wraps
from pydantic import BaseModel, EmailStr, HttpUrl
from pydantic_settings import BaseSettings

from dotenv import load_dotenv

load_dotenv('.env')

with open('./config/settings.toml', 'r') as config_toml:
    toml_config = toml.load(config_toml)

class UserCredentialsConfig(BaseModel):
    """
    Represents user credentials with email and password.
    Validates the email format using Pydantic's EmailStr and defines the structure
    for user credentials.
    """
    email: EmailStr
    password: str
    
    class Config:
        toml_prefix = 'login'
        env_file = '.env'
        extra = "ignore"

class FloofyPagesConfig(BaseSettings):
    base: str
    intake_ny: str
    intake_la: str
    intake_fl: str

    class Config:
        env_prefix = 'FLOOFY_'
        env_file = '.env'
        extra = "ignore"

class MetaPagesConfig(BaseSettings):
    base: str
    allpharm: str
    realtime: str
    vet_orders: str

    class Config:
        env_prefix = 'META_'
        env_file = '.env'
        extra = "ignore"

class SlackConfig(BaseSettings):
    channel_id: str
    token: str

    class Config:
        env_prefix = 'SLACK_'
        env_file = '.env'
        extra = "ignore"


EMAIL = os.getenv('EMAIL')

login_config = UserCredentialsConfig(email=EMAIL, 
                                     password= kr.get_password(service_name=os.getenv('SERVICE_ID'),username=EMAIL))
 
meta_config = MetaPagesConfig()
floofy_config = FloofyPagesConfig()
slack_config = SlackConfig()




if __name__ == '__main__':
    pass