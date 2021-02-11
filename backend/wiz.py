#!/usr/bin/python3

import os
import inspect
import ast
import logging
log = logging.getLogger(__name__)

from blockchain import trustframework as tf
from blockchain import wallet, certificates, safeisland, eutl
from blockchain import christmas, compile

from settings import settings


##########################################################################
# The menu support routines
##########################################################################

class Menu(object):
    def __init__(self, options=None, title=None, message=None, prompt=">>>",
                 refresh=lambda: None, auto_clear=True):
        if options is None:
            options = []
        self.options = None
        self.title = None
        self.is_title_enabled = None
        self.message = None
        self.is_message_enabled = None
        self.refresh = None
        self.prompt = None
        self.is_open = None
        self.auto_clear = auto_clear
        
        self.set_options(options)
        self.set_title(title)
        self.set_title_enabled(title is not None)
        self.set_message(message)
        self.set_message_enabled(message is not None)
        self.set_prompt(prompt)
        self.set_refresh(refresh)

    def set_options(self, options):
        original = self.options
        self.options = []
        try:
            for option in options:
                if not isinstance(option, tuple):
                    raise TypeError(option, "option is not a tuple")
                if len(option) < 2:
                    raise ValueError(option, "option is missing a handler")
                kwargs = option[2] if len(option) == 3 else {}
                self.add_option(option[0], option[1], kwargs)
        except (TypeError, ValueError) as e:
            self.options = original
            raise e

    def set_title(self, title):
        self.title = title

    def set_title_enabled(self, is_enabled):
        self.is_title_enabled = is_enabled

    def set_message(self, message):
        self.message = message

    def set_message_enabled(self, is_enabled):
        self.is_message_enabled = is_enabled

    def set_prompt(self, prompt):
        self.prompt = prompt

    def set_refresh(self, refresh):
        if not callable(refresh):
            raise TypeError(refresh, "refresh is not callable")
        self.refresh = refresh

    def add_option(self, name, handler, kwargs):
        if not callable(handler):
            raise TypeError(handler, "handler is not callable")
        self.options += [(name, handler, kwargs)]

    # open the menu
    def open(self):
        self.is_open = True
        while self.is_open:
            self.refresh()
            func = self.input()
            if func == Menu.CLOSE:
                func = self.close
            print()
            func()

    def close(self):
        self.is_open = False

    # clear the screen
    # show the options
    def show(self):
        if self.auto_clear:
            os.system('cls' if os.name == 'nt' else 'clear')
        if self.is_title_enabled:
            print(self.title)
            print()
        if self.is_message_enabled:
            print(self.message)
            print()
        for (index, option) in enumerate(self.options):
            print(str(index + 1) + ". " + option[0])
        print("ENTER to exit")
        print()

    # show the menu
    # get the option index from the input
    # return the corresponding option handler
    def input(self):
        if len(self.options) == 0:
            return Menu.CLOSE
        try:
            self.show()
            inp = input(self.prompt + " ")
            if inp == "":
                return Menu.CLOSE
            index = int(inp) - 1
            option = self.options[index]
            handler = option[1]
            if handler == Menu.CLOSE:
                return Menu.CLOSE
            kwargs = option[2]
            return lambda: handler(**kwargs)
        except (ValueError, IndexError):
            return self.input()

    def CLOSE(self):
        pass


def get_arguments(argument_definitions):

    arguments = []
    for arg in argument_definitions:

        name = arg["name"]
        prompt = arg["prompt"]
        # Get the argument type, with default str if the key does not exist
        arg_type = arg.get("type", "str")

        if arg_type == "bool":
            if arg["default"] == True:
                prompt = prompt + " [Y/n]"
            else:
                prompt = prompt + " [N/y]"

        if arg_type == "str":
            prompt = prompt + " [" + arg.get("default", "") + "]"

        prompt = prompt + ": "
        
        s = input(prompt)

        if s == "":
            s = arg["default"]

        if arg_type == "bool":
            true_values = (True, "Y", "y")
            if s in true_values:
                s = True
            else:
                s = False

        arguments.append(s)
    
    return arguments

def invoke(operation):
    # Check if the operation is a function
    if not inspect.isfunction(operation):
        log.error(f"{operation} is not a function")
        input("Press a key")
        return

    # Get the docstring and split in lines
    doc = inspect.getdoc(operation)

    # Signal error if the function does not have a docstring
    if doc is None or len(doc) == 0:
        log.error(f"Missing docstring in {operation}")
        input("Press a key")
        return

    doc_lines = doc.splitlines()

    # The docstring should be formatted in a specific way.
    # The first lines are the "normal" function documentation
    # Then a separator, exactly as: "--- Definitions ---"
    # Finally, one line per argument, formatted as a dict:
    # {"name": "compile", "type": "bool", "prompt": "Compile contracts?", "default": True}
    # If the separator line does not exist or no definitions, assume the function has zero arguments

    docs = []
    argument_definitions = []
    separator_found = False
    for l in doc_lines:
        if l == "--- Definitions ---":
            separator_found = True
            continue
        if separator_found:
            p = ast.literal_eval(l)
            argument_definitions.append(p)
        else:
            docs.append(l)
    
    # Print the comment of the function
    for l in docs:
        print(l)

    args = get_arguments(argument_definitions)
    operation(*args)

    input("\nPress enter to continue")



##########################################################################
##########################################################################
# The Main Interactive Menu
##########################################################################
##########################################################################

def main_menu():

    warning_message = ""
    try:
        tf.connect_blockchain(settings.BLOCKCHAIN_NODE_IP)
    except FileNotFoundError as e:
        print(e)
        warning_message = "[ATTENTION: no deployment artifacts found. Deploy Smart Contracts first] - "

    blk_ip = settings.BLOCKCHAIN_NODE_IP
    warning_message = blk_ip + " " + warning_message
    main = Menu(title = warning_message + "Public Credentials Maintenance")

    identities = Menu(title = "Identities")
    identities.set_options([
        ("Create/Update an Identity", invoke, {"operation":tf.m_create_identity}),
        ("Resolve a DID", invoke, {"operation":tf.m_get_DIDDocument}),
        ("Dump all identities", invoke, {"operation":tf.m_dump_all_identities}),
    ])

    wallet_menu = Menu(title = "Wallet")
    wallet_menu.set_options([
        ("Create/Update an account", invoke, {"operation":wallet.m_create_account}),
        ("Query an account", invoke, {"operation":wallet.m_get_address}),
        ("List all accounts", invoke, {"operation":tf.m_dump_all_identities}),
    ])

    node_management = Menu(title = "Listings of the Trust system")
    node_management.set_options([
        ("Gets the owner of a given node in Alastria ENS", invoke, {"operation":tf.m_get_owner}),
        ("Get a subnode of a given node", invoke, {"operation":tf.m_get_subnode}),
        ("Set the name of a node for reverse resolution", invoke, {"operation":tf.m_setName}),
        ("Get the name assigned to a node", invoke, {"operation":tf.m_getName}),
    ])

    trusted_lists = Menu(title = "Trusted Lists")
    trusted_lists.set_options([
        ("Import into table the EU LOTL info", invoke, {"operation":eutl.m_import_eulotl_db}),
        ("Import into table the Spanish Trusted List", invoke, {"operation":eutl.m_import_estl_db}),
        ("Create in blockchain the EU List of Trusted Lists", invoke, {"operation":eutl.m_lotl}),
        ("Display from blockchain the Spanish Trusted List", invoke, {"operation":eutl.m_lotl_dump}),
    ])


    credentials = Menu(title = "COVID19 Credentials")
    credentials.set_options([
        ("Erase Covid19 database", invoke, {"operation":safeisland.erase_db}),
        ("Create a Covid19 certificate", invoke, {"operation":safeisland.m_new_certificate}),
        ("Create a Vaccination certificate", invoke, {"operation":safeisland.m_new_vaccination_certificate}),
        ("Display a Covid19 certificate", invoke, {"operation":safeisland.m_certificate}),
        ("Bootstrap Test credentials", invoke, {"operation":safeisland.create_test_credentials}),
        ("List all certificates", invoke, {"operation":safeisland.m_list_certificates}),
    ])

    christmas_menu = Menu(title = "Christmas")
    christmas_menu.set_options([
        ("Erase Christmas table", invoke, {"operation":christmas.erase_db}),
        ("Create identities of companies", invoke, {"operation":christmas.m_create_identities}),
        ("Create Christmas credentials", invoke, {"operation":christmas.m_create_credentials}),
        ("Create a Christmas certificate", invoke, {"operation":christmas.m_new_certificate}),
        ("Display a Christmas certificate", invoke, {"operation":christmas.m_certificate}),
        ("List all Christmas certificates", invoke, {"operation":christmas.m_list_certificates}),
    ])


    main.set_options([
        ("Compile the Smart Contracts", invoke, {"operation":compile.m_compile}),
        ("Deploy the Smart Contracts", invoke, {"operation":compile.m_deploy}),
        ("Bootstrap Identity Framework (Top Level Domain)", invoke, {"operation":tf.m_create_test_identities}),
        ("Bootstrap Credentials Framework", invoke, {"operation":tf.m_create_test_pubcred}),
        ("Identities", identities.open),
        ("COVID19 Credentials", credentials.open),
        ("Trusted Lists", trusted_lists.open),
        ("Wallet (management of private keys)", wallet_menu.open),
        ("Node management", node_management.open),
        ("Cesta de Navidad", christmas_menu.open),        
    ])

    main.open()


if __name__ == '__main__':

    main_menu()
    