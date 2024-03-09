import os
import logging
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackComs:
    """
    A class to handle communications with Slack, including sending messages and uploading files.
    """

    def __init__(self, token:str, channel:str):
        self.client = WebClient(token=token)
        self.channel = channel
        # self.validate_token()

    def validate_token(self):
        """
        Validates the Slack token by making a test API call.
        """
        try:
            response = self.client.auth_test()
            logging.info(f"Slack token validation successful: {response}")
        except SlackApiError as e:
            logging.error(f"Invalid Slack token: {str(e)}")
            raise ValueError("Invalid Slack token.")

    def upload(self, file_path: str, title: str|None = None, initial_comment: str|None = None) -> None:
        """
        Uploads a file to a Slack channel.
        :param file_path: Path to the file to upload.
        :param title: Title of the file.
        :param initial_comment: Initial comment to post with the file.
        """
        if not os.path.exists(file_path):
            logging.error(f'File not found: {file_path}')
            return

        try:
            response = self.client.files_upload_v2(
                channel=self.channel,
                title=title,
                file=file_path,
                initial_comment=initial_comment
            )
            logging.info(f'Successfully sent file to Slack with file: {file_path}')
            logging.debug(f'Slack response: {response}')
        except SlackApiError as e:
            logging.error(f'Error sending file to Slack: {str(e)}')

    def post(self, message: str) -> None:
        """
        Posts a message to a Slack channel.
        :param message: The message to post.
        """
        if not message:
            logging.error('Message is empty')
            return

        try:
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=message
            )
            logging.info(f'Successfully sent message to Slack: {message}')
            logging.debug(f'Slack response: {response}')
        except SlackApiError as e:
            logging.error(f'Error sending message to Slack: {str(e)}')


if __name__ == '__main__':
    pass