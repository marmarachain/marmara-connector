import csv
import os
from appdirs import *
from configparser import ConfigParser, Error
import remote_connection
from fbs_runtime.application_context.PyQt5 import ApplicationContext

app_name = ApplicationContext().build_settings['app_name']
author = ApplicationContext().build_settings['author']
version = ApplicationContext().build_settings['version']

resource_path = ApplicationContext().get_resource("configuration")

# Typical user config directories are:
#   Mac OS X:             ~/Library/Application Support/<AppName>
#   Unix:                 ~/.config/<AppName>     # or in $XDG_CONFIG_HOME, if defined
#   Win XP (roaming):     C:\Documents and Settings\<username>\Local Settings\Application Data\<AppAuthor>\<AppName>
#   Win 7  (roaming):     C:\Users\<username>\AppData\Roaming\<AppAuthor>\<AppName>
config_directory_path = user_config_dir(app_name, author, version, roaming=True)


class ApplicationConfig:
    config_file = "marmara-connector.conf"
    # make platform-specific config directory to store config and log files
    os.makedirs(config_directory_path, exist_ok=True)
    config_file_path = os.path.join(config_directory_path, config_file)

    def __init__(self):
        # create config object
        self.config = ConfigParser()

    def check_conf_exists(self):
        if not os.path.exists(self.config_file_path) or os.stat(self.config_file_path).st_size == 0:
            with open(self.config_file_path, 'w') as configfile:
                self.config.add_section('PATHS')
                self.config.add_section('USER')
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
            return e


class ConnectorConf:
    marmara_connector_conf = resource_path + "/mclconnector.conf"

    def is_conf_exist(self):
        if os.path.isfile(self.marmara_connector_conf):
            return
        else:
            try:
                file = open(self.marmara_connector_conf, 'w')
            except IOError:
                print("Exception error when writing conf file!")
            finally:
                file.close()

    def write_conf_file(self, conf_key, conf_value):
        try:
            conf_file = open(self.marmara_connector_conf, 'w')
            conf_data = conf_key + "=" + conf_value + "\n"
            conf_file.write(conf_data)
        except IOError:
            print("Exception error while writing conf file!")
        finally:
            conf_file.close()

    def read_conf_file(self):
        self.is_conf_exist()
        data_dict = {}
        try:
            conf_file = open(self.marmara_connector_conf, 'r')
            conf_data = conf_file.read().split("\n")
            for data in conf_data:
                data_split = data.split('=')
                if not data_split == ['']:
                    key = data_split[0]
                    value = data_split[1]
                    data_dict.__setitem__(key, value)
        except IOError:
            print("Exception error while reading conf file!")
        finally:
            conf_file.close()
        return data_dict


user_data_path = user_data_dir(app_name, author, version, roaming=True)
# Typical user data directories are:
#     Mac OS X:               ~/Library/Application Support/<AppName>
#     Unix:                   ~/.local/share/<AppName>    # or in $XDG_DATA_HOME, if defined
#     Win XP (roaming=True):  C:\Documents and Settings\<username>\Local Settings\Application Data\<AppAuthor>\<AppName>
#     Win 7  (roaming=True):  C:\Users\<username>\AppData\Roaming\<AppAuthor>\<AppName>

os.makedirs(user_data_path, exist_ok=True)  # make platform-specific user directory to store user data files


class ServerSettings:
    server_conf_file = "servers.info"
    server_config_file_path = os.path.join(user_data_path, server_conf_file)
    print("server_config_file_path located in: " + server_config_file_path)

    # Create the file if it does not exist
    if not os.path.exists(server_config_file_path) or os.stat(server_config_file_path).st_size == 0:
        open(server_config_file_path, 'a+').close()

    def save_file(self, server_name, server_username, server_ip):
        try:
            file = open(self.server_config_file_path, 'a')
            server_params = server_name + "," + server_username + "," + server_ip + "\n"
            file.write(server_params)
        except IOError:
            print("Exception error while reading server file!")
        finally:
            file.close()

    def read_file(self):
        server_list = []
        if os.stat(self.server_config_file_path).st_size != 0:
            try:
                file = open(self.server_config_file_path, "r")
                server_all_info = file.read().rstrip()
                server_list = server_all_info.split("\n")
            except IOError:
                print("Exception error while reading server file!")
            finally:
                file.close()
        return server_list

    def delete_record(self, server_list):
        print(server_list)
        try:
            file = open(self.server_config_file_path, 'w')
            for line in server_list:
                file.write(line + "\n")
        except IOError:
            print("Exception error when reading server file!")
        finally:
            file.close()


class ContactsSettings:
    # contacts_file = resource_path + '/contacts.csv'
    contacts_file = "contacts.csv"
    header = ['Name', 'Address', 'Pubkey']
    contacts_file_path = os.path.join(user_data_path, contacts_file)
    print("contacts_file_path located in: " + contacts_file_path)

    def is_file_exist(self):
        if os.path.isfile(self.contacts_file_path):
            return
        else:
            print('no file found')
            self.create_csv_file()
            print('contacts file created')
            return

    def read_csv_file(self):
        self.is_file_exist()
        contactdata = open(self.contacts_file_path, 'r')
        contactdatadata_reader = csv.reader(contactdata)
        contactdatadata_list = []
        for row in contactdatadata_reader:
            contactdatadata_list.append(row)
        contactdata.close()
        return contactdatadata_list

    def create_csv_file(self):
        contacts_csv = open(self.contacts_file_path, 'w', newline='')
        create = csv.writer(contacts_csv)
        create.writerow(self.header)

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
