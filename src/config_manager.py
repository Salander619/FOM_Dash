"""
Manage the configuration file 
in order to provide the correct data to the application
"""

import configparser

class ConfigManager:
    """
    Read and store the different configuration and data from the ini file
    i0n order to ensure consistency between both.
    """

    def __init__(self, section):
        """
        Initialize the configManager with the name of the page 
        in order to get the correct section in the ini file

        :param string section: name of the desired section
        """
        self.config = configparser.ConfigParser()
        self.config.read("data/configuration.ini")

        self.section = section
        self.required_parameters = self.section.count('.')

        # If the data file rely on 2 parameters
        if self.required_parameters == 2:

            self.data_files = []
            self.configurations = []

            # Initialize the lists
            for key in self.config[self.section]:
                value_as_list = self.parse_config(
                    self.config[self.section][key]
                )
                self.data_files.append(value_as_list[-1])
                self.configurations.append(self.parse_tuple(value_as_list[0]))
        else:
            self.data_files = []
            self.configurations = []

            # Initialize the lists
            for key in self.config[self.section]:
                self.data_files.append(self.config[self.section][key])
                self.configurations.append(key)

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

    def get_data_file(self, config):
        """
        Return the datafile at the index of the tuple passed as an argument

        :param string/tuple config: configuration

        :return string: path to datafile corresponding to the configuration
        """
        for i, _ in enumerate(self.configurations):
            if config == self.configurations[i]:
                return self.data_files[i]

        # if no matching config have been found
        return self.data_files[0]
