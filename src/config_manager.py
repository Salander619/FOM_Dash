"""
Manage the configuration file 
in order to provide the correct data to the application
"""

import configparser

class ConfigManager:
    """
    Read and store the different configuration and data from the ini file
    in order to ensure consistency between both.
    """

    def __init__(self, path_2_ini_file):
        self.config = configparser.ConfigParser()
        self.config.read(path_2_ini_file)

    def get_data_file(self, section_name, config_name):
        """
        Return the datafile at the index of the tuple passed as an argument

        :param string section_name: name of the desired section
        :param string/tuple config_name: name of the desired configuration

        :return string: path to datafile corresponding to the configuration
        """
        for option in self.config[section_name]:
            if self.is_tuple(option):
                config_2_check = self.parse_tuple(option)
            else:
                config_2_check = option

            if config_2_check == config_name:
                return self.config[section_name][option]

        raise ValueError("""The configuration asked for is 
                         not contained in the configuration file""")

    def is_tuple(self, input_string):
        """
        Return if the input string is written with the tuple syntax 
        (with parenthesis and a comma)

        :param strin input_string: the string to analyse

        :return boolean: True is the input's syntax is correct 
        and False otherwise
        """

        size = len(input_string)
        if (input_string.startswith("(",0,1)
           and input_string.startswith(")",size-1,size)
           and "," in input_string):
            return True

        return False

    def parse_config(self,input_string):
        """
        Parse the value string found in the ini file

        :param string input_string: string to parse along the ':' character

        :return list: element in value string separated by ':'
        """
        return input_string.split(":")

    # Source:
    # https://stackoverflow.com/questions/56967754/how-to-store-and-retrieve-a-dictionary-of-tuples-in-config-parser-python
    def parse_tuple(self,input_string):
        """
        Parse a string as a tuple

        :param string input_string: string to convert as a tuple
        
        :return tuple: tuple containing noise configuration
         and mission duration
        """
        return tuple(k.strip() for k in input_string[1:-1].split(','))
