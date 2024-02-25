import logging
import toml

with open('./config/settings.toml', 'r') as log_config:
    
    log = toml.load(log_config)['logging']

    logging.basicConfig(filemode=log['filename'],
                        level=eval(log['level']),
                        format=log['format']
                        )