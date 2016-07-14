"""This module allows users to write journal articles,
and to store them in and retrieve them from a SQLite database"""

__version__ = '0.1'
__author__ = 'Matthew Hill'

from datetime import datetime
from time import sleep
import os
import sys

from peewee import *


APP_INSTRUCTIONS = """
Enter (C)reate to make a new entry
Enter (V)iew to view entries
Enter (Q)uit once you are finished
"""

CREATE_INSTRUCTIONS = """
Enter your journal entry.
On a new line type ctrl+{}, then press enter when you are finished.
""".format('z' if os.name == 'nt' else 'd')

VIEW_INSTRUCTIONS = """
Enter (O)lder to view older entries
Enter (N)ewer to view newer entries
Enter (D)elete to delete this entry
Enter (Q)uit to return to main menu
"""

VALID_INPUTS = {'home': ['C', 'V', 'Q'],
                'view': ['O', 'N', 'D', 'Q'],
                'yes_no': ['Y', 'N'],
                }


db = SqliteDatabase('myjournal.db')


class BaseModel(Model):
    """All models inherit the Meta class"""
    class Meta:
        database = db


class Entry(BaseModel):
    """Model class for all journal entries"""
    created = DateTimeField(default=datetime.now)
    title = CharField(max_length=80)
    contents = TextField()


# Connect to db and create table if they don't already exist
db.connect()
db.create_tables([Entry], safe=True)


def clear():
    """Command to os to clear screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def validate_input(user_input, input_type):
    """Checks to see if user has input an appropriate value, then converts it"""
    if user_input and user_input.strip()[0].upper() in VALID_INPUTS[input_type]:
        return user_input.strip()[0].upper()
    else:
        return None


def create_entry():
    """Allows user to create a new journal entry"""
    clear()
    title = input("Enter a title for your journal entry\n> ")
    print(CREATE_INSTRUCTIONS)

    contents = sys.stdin.read().strip()
    if validate_input(input("Save?\nY/n? "), 'yes_no') != 'N':
        Entry.create(title=title, contents=contents)
    main_menu()


def older_entry(number):
    """Allows user to view the next entry by date"""
    if number >= (Entry.select().count())-1:
        print("This is the last entry!")
        sleep(1)
        view_entries(number)
    else:
        view_entries(number+1)


def newer_entry(number):
    """Allows user to view the previous entry by date"""
    if number == 0:
        print("This is the latest entry!")
        sleep(1)
        view_entries(number)
    else:
        view_entries(number-1)


def delete_entry(number, entry):
    """Allows user to delete the current entry"""
    print("Are you sure you wish to delete this entry?")
    response = input("y/N ")
    response = validate_input(response, 'yes_no')
    if response != 'Y':
        view_entries(number)
    else:
        entry.delete_instance()
        print("Entry deleted!")
        sleep(1)
        main_menu()


def view_entries(number=0):
    """Displays an entry to the user, default is most current unless number is specified"""
    clear()
    entry = Entry.select().order_by(-Entry.created)[number]
    print(entry.title)
    print(entry.created.strftime('%d %B %Y'))
    print('\n'+entry.contents+'\n')
    print(VIEW_INSTRUCTIONS)

    # Request and validate user input
    user_input = validate_input(input("> "), 'view')
    if not user_input:
        print("Please enter a valid input!")
        sleep(1)
        view_entries(number)

    elif user_input == 'O':
        older_entry(number)
    elif user_input == 'N':
        newer_entry(number)
    elif user_input == 'D':
        delete_entry(number, entry)
    else:
        main_menu()


def main_menu():
    """The main loop.
    Requests input from the user and returns the corresponding function"""
    clear()
    print("Journal App")
    print(APP_INSTRUCTIONS)

    # Request and validate user input
    user_input = validate_input(input("> "), 'home')
    if not user_input:
        print("That's not a valid input!")
        sleep(1)
        main_menu()

    # User wishes to create new entry
    elif user_input == 'C':
        create_entry()

    # User wishes to view old entries
    elif user_input == 'V':
        if Entry.select().count() == 0:
            print("You haven't written anything yet!")
            sleep(1)
            main_menu()
        else:
            view_entries()

    # User wishes to quit program
    else:
        db.close()
        print("Goodbye")
        sleep(1)
        sys.exit()


if __name__ == "__main__":
    main_menu()
