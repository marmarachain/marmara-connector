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
