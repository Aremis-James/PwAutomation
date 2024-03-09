import os
from pydantic import BaseModel, EmailStr
from pydantic_settings import BaseSettings
from dopplersdk import DopplerSDK
from dotenv import load_dotenv

load_dotenv('.env')


def doppler_config_secrets(secret_name:str, project:str = 'mixlab-scrapper', dev_config:str = 'dev_aremis-james'):
    _sdk = DopplerSDK()
    _sdk.set_access_token(os.getenv('DOPPLER_TOKEN'))
    results = _sdk.secrets.get(
         project=project,
         config=dev_config,
         name=secret_name
    )
    return vars(results)['value']['raw']

EMAIL = doppler_config_secrets('EMAIL')

KEY = doppler_config_secrets('ENCRYPTION_KEY').encode()


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


if __name__ == "__main__":
    print(os.listdir())