import csv
import os

from fbs_runtime.application_context.PyQt5 import ApplicationContext

resource_path = ApplicationContext().get_resource("configuration")


class ServerSettings:
    server_conf_file = resource_path + "/servers.info"

    def save_file(self, server_name, server_username, server_ip):
        try:
            file = open(self.server_conf_file, 'a')
            server_params = server_name + "," + server_username + "," + server_ip + "\n"
            file.write(server_params)
        except IOError:
            print("Exception error while reading server file!")
        finally:
            file.close()

    def read_file(self):
        server_list = []
        if os.stat(self.server_conf_file).st_size != 0:
            if os.path.isfile(self.server_conf_file):
                try:
                    file = open(self.server_conf_file, "r")
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
            file = open(self.server_conf_file, 'w')
            for line in server_list:
                file.write(line + "\n")
        except IOError:
            print("Exception error when reading server file!")
        finally:
            file.close()


class ContacstSettings:
    contacts_file = resource_path + '/contacts.csv'
    header = ['Name', 'Address', 'Pubkey']

    def is_file_exist(self):
        if os.path.isfile(self.contacts_file):
            return
        else:
            print('no file')
            self.create_csv_file()
            print('file created')
            return

    def read_csv_file(self):
        self.is_file_exist()
        contactdata = open(self.contacts_file, 'r')
        contactdatadata_reader = csv.reader(contactdata)
        contactdatadata_list = []
        for row in contactdatadata_reader:
            contactdatadata_list.append(row)
        contactdata.close()
        return contactdatadata_list

    def create_csv_file(self):
        contacts_csv = open(self.contacts_file, 'w', newline='')
        create = csv.writer(contacts_csv)
        create.writerow(self.header)

    def add_csv_file(self, row):
        if not os.path.isfile(self.contacts_file):
            self.create_csv_file()
        contacts_csv = open(self.contacts_file, 'a', newline='')
        contacts_csv_writer = csv.writer(contacts_csv)
        contacts_csv_writer.writerow(row)
        contacts_csv.close()

    def update_csv_file(self, contact_csv_list):
        contacts_csv = open(self.contacts_file, 'w', newline='')
        create = csv.writer(contacts_csv)
        create.writerows(contact_csv_list)

