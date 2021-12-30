import csv
import os
from appdirs import *
from configparser import ConfigParser, Error
from fbs_runtime.application_context.PyQt5 import ApplicationContext
import logging

app_name = ApplicationContext().build_settings['app_name']
author = ApplicationContext().build_settings['author']
version = ApplicationContext().build_settings['version']
configuration_path = ApplicationContext().get_resource("configuration")

config_directory_path = user_config_dir(app_name, author, version, roaming=True)
os.makedirs(config_directory_path, exist_ok=True)  # make platform-specific config directory to store config & log files
# Typical user config directories are:
#   Mac OS X:             ~/Library/Application Support/<AppName>
#   Unix:                 ~/.config/<AppName>     # or in $XDG_CONFIG_HOME, if defined
#   Win XP (roaming):     C:\Documents and Settings\<username>\Local Settings\Application Data\<AppAuthor>\<AppName>
#   Win 7  (roaming):     C:\Users\<username>\AppData\Roaming\<AppAuthor>\<AppName>
user_data_path = user_data_dir(app_name, author, roaming=True)
os.makedirs(user_data_path, exist_ok=True)  # make platform-specific user directory to store user data files
# Typical user data directories are:
#     Mac OS X:               ~/Library/Application Support/<AppName>
#     Unix:                   ~/.local/share/<AppName>    # or in $XDG_DATA_HOME, if defined
#     Win XP (roaming=True):  C:\Documents and Settings\<username>\Local Settings\Application Data\<AppAuthor>\<AppName>
#     Win 7  (roaming=True):  C:\Users\<username>\AppData\Roaming\<AppAuthor>\<AppName>

log_file_path = os.path.join(config_directory_path, "marmara-connector.log")  # configure log file directory
logging.getLogger(__name__)
stream_handler = logging.StreamHandler()  # create stream handler and set level to info
stream_handler.setLevel(logging.INFO)  # set stream handler level to info
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s:%(module)s %(funcName)s:%(lineno)s %(message)s',
                    handlers=[logging.FileHandler(filename=log_file_path, mode='a+'), stream_handler])


class ApplicationConfig:
    config_file = "marmara-connector.conf"
    config_file_path = os.path.join(config_directory_path, config_file)

    def __init__(self):
        # create config object
        self.config = ConfigParser()

    def check_conf_exists(self):
        if not os.path.exists(self.config_file_path) or os.stat(self.config_file_path).st_size == 0:
            with open(self.config_file_path, 'w') as configfile:
                self.config.add_section('PATHS')
                self.config.add_section('USER')
                self.config.set('USER', 'lang', 'EN')
                self.config.set('USER', 'style', 'light')
                self.config.set('USER', 'fontsize', '12')
                self.config.write(configfile)

    def set_key_value(self, section, key, value):
        self.check_conf_exists()
        # reading config file
        self.config.read(self.config_file_path)
        # Write the structure to the new file
        with open(self.config_file_path, 'w') as configfile:
            self.config.set(section, key, value)
            self.config.write(configfile)

    def get_value(self, section, key):
        self.check_conf_exists()
        self.config.read(self.config_file_path)
        try:
            value = self.config.get(section, key)
            return value
        except Error as e:
            logging.error(e)
            return False


class ServerSettings:
    server_conf_file = "servers.info"
    server_config_file_path = os.path.join(user_data_path, server_conf_file)

    # Create the file if it does not exist
    if not os.path.exists(server_config_file_path) or os.stat(server_config_file_path).st_size == 0:
        open(server_config_file_path, 'a+').close()

    def save_file(self, server_name, server_username, server_ip):
        try:
            file = open(self.server_config_file_path, 'a')
            server_params = server_name + "," + server_username + "," + server_ip + "\n"
            file.write(server_params)
        except IOError as error:
            logging.error("Exception error while reading server file: " + error)
        finally:
            file.close()

    def read_file(self):
        server_list = []
        if os.stat(self.server_config_file_path).st_size != 0:
            try:
                file = open(self.server_config_file_path, "r")
                server_all_info = file.read().rstrip()
                server_list = server_all_info.split("\n")
            except IOError as error:
                logging.error("Exception error while reading server file: " + error)
            finally:
                file.close()
        return server_list

    def delete_record(self, server_list):
        try:
            file = open(self.server_config_file_path, 'w')
            for line in server_list:
                file.write(line + "\n")
        except IOError as error:
            logging.error("Exception error while reading server file: " + error)
        finally:
            file.close()


class ContactsSettings:
    contacts_file = "contacts.csv"
    header = ['Name', 'Address', 'Pubkey', 'Group']
    contacts_file_path = os.path.join(user_data_path, contacts_file)

    def create_csv_file(self):
        contacts_csv = open(self.contacts_file_path, 'w', newline='')
        create = csv.writer(contacts_csv)
        create.writerow(self.header)

    def is_file_exist(self):
        if os.path.isfile(self.contacts_file_path):
            return
        else:
            logging.warning('No contacts file found under ' + user_data_path)
            self.create_csv_file()
            logging.info('Contacts file named ' + self.contacts_file + 'is created under ' + user_data_path)
            return

    def read_csv_file(self):
        self.is_file_exist()
        contact_data = open(self.contacts_file_path, 'r')
        contact_data_reader = csv.reader(contact_data)
        contact_data_list = []
        for row in contact_data_reader:
            contact_data_list.append(row)
        contact_data.close()
        return contact_data_list

    def add_csv_file(self, row):
        if not os.path.isfile(self.contacts_file_path):
            self.create_csv_file()
        contacts_csv = open(self.contacts_file_path, 'a', newline='')
        contacts_csv_writer = csv.writer(contacts_csv)
        contacts_csv_writer.writerow(row)
        contacts_csv.close()

    def update_csv_file(self, contact_csv_list):
        contacts_csv = open(self.contacts_file_path, 'w', newline='')
        create = csv.writer(contacts_csv)
        create.writerows(contact_csv_list)
