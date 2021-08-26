

import sqlite3
import random
from sqlite3.dbapi2 import Connection

conn: Connection = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS card (
id INTEGER,
number TEXT,
pin TEXT,
balance INTEGER DEFAULT 0);''')
conn.commit()

exit_ = "off"


def new_card():

    # generate card number (int)
    card_number = 4_000_000_000_000_000 + random.randint(10, 99_999_999) * 10

    # adding luhn digit
    card_num_list = [int(x) for x in list(str(card_number))]
    luhn_list = []
    for i in range(16):
        if i % 2 == 0:
            if card_num_list[i] * 2 > 9:
                luhn_list.append(card_num_list[i] * 2 - 9)
            else:
                luhn_list.append(card_num_list[i] * 2)
        else:
            luhn_list.append(card_num_list[i])

    if 10 - sum(luhn_list) % 10 != 10:
        card_number += 10 - sum(luhn_list) % 10

    print("\n\nYour card has been created\nYour card number:\n" + str(card_number))

    # generate pin (str)
    pin = ""
    for i in range(4):
        pin += str(random.randint(0, 9))
    print("Your card PIN:\n" + pin)

    # store details
    sql_command_store = """INSERT INTO card (number, pin) VALUES (?,?);"""
    cur.execute(sql_command_store, (str(card_number), pin))
    conn.commit()


def luhn_check(number_check):

    card_num_list = [int(x) for x in list(str(number_check))]
    luhn_list = []
    for i in range(15):
        if i % 2 == 0:
            if card_num_list[i] * 2 > 9:
                luhn_list.append(card_num_list[i] * 2 - 9)
            else:
                luhn_list.append(card_num_list[i] * 2)
        else:
            luhn_list.append(card_num_list[i])
    luhn_list.append(0)

    if 10 - sum(luhn_list) % 10 != 10:
        luhn_number = 10 - sum(luhn_list) % 10
    else:
        luhn_number = 0

    return luhn_number == card_num_list[15]


def login_check():

    # check login
    card_entered = input("\n\nEnter your card number:\n")
    pin_entered = input("Enter your PIN:\n")

    sql_command_login_check = """SELECT count(*) FROM card WHERE number = ? AND pin = ?;"""
    cur.execute(sql_command_login_check, (card_entered, pin_entered))
    if cur.fetchall()[0][0] > 0:
        print("\n\nYou have successfully logged in!")
        conn.commit()
        logged_in(card_entered)
    else:
        print("\n\nWrong card number or PIN!")
        conn.commit()


def logged_in(card_number):

    global exit_

    login_option = int(input("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n"))

    if login_option == 1:
        # show balance
        sql_command_balance = """SELECT balance FROM card WHERE number = ?;"""
        cur.execute(sql_command_balance, (card_number,))
        balance = cur.fetchall()[0][0]
        conn.commit()
        print("\n\nBalance: " + str(balance))
        logged_in(card_number)

    elif login_option == 2:
        # add income
        add_income(card_number)

    elif login_option == 3:
        # do transfer
        transfer(card_number)

    elif login_option == 4:
        # close account
        close_account(card_number)

    elif login_option == 5:
        # log out
        print("\n\nYou have successfully logged out!")

    elif login_option == 0:
        # exit
        exit_ = "on"


def transfer(card_number):

    transfer_to = int(input("Enter card number:\n"))

    # validity checks

    # 1 - transfer same account
    if transfer_to == card_number:
        print("You can't transfer money to the same account!\n")
        logged_in(card_number)

    # 2 - transfer to luhn check
    if not luhn_check(transfer_to):
        print("Probably you made mistake in the card number. Please try again!\n")
        logged_in(card_number)
    else:
        # 3 - transfer to exists
        sql_command_exists = """SELECT count(*) FROM card WHERE number = ?;"""
        cur.execute(sql_command_exists, (transfer_to,))
        conn.commit()

        if cur.fetchall()[0][0] == 0:
            print("Such a card does not exist.\n")
            logged_in(card_number)
        else:
            # 4 - transfer from balance
            transfer_amount = int(input("Enter how much money you want to transfer:\n"))

            sql_command_check_bal = """SELECT balance FROM card WHERE number = ?;"""
            cur.execute(sql_command_check_bal, (card_number,))
            check_balance = cur.fetchall()[0][0]
            conn.commit()

            if check_balance < transfer_amount:
                print("Not enough money!\n")
                logged_in(card_number)
            else:
                # validity checks passed - proceed to transfer funds

                # transfer from - delete funds
                sql_command_temp_bal_from = """SELECT balance FROM card WHERE number = ?;"""
                cur.execute(sql_command_temp_bal_from, (card_number,))
                temp_balance = cur.fetchall()[0][0]
                temp_balance -= transfer_amount
                conn.commit()

                sql_command_new_bal_from = """UPDATE card SET balance = ? WHERE number = ?;"""
                cur.execute(sql_command_new_bal_from, (temp_balance, card_number))
                conn.commit()

                # transfer to - add funds
                sql_command_temp_bal_to = """SELECT balance FROM card WHERE number = ?;"""
                cur.execute(sql_command_temp_bal_to, (str(transfer_to),))
                temp_balance = cur.fetchall()[0][0]
                temp_balance += transfer_amount
                conn.commit()

                sql_command_new_bal_to = """UPDATE card SET balance = ? WHERE number = ?;"""
                cur.execute(sql_command_new_bal_to, (temp_balance, str(transfer_to)))
                conn.commit()

                print("Success!\n")
                logged_in(card_number)


def add_income(card_number):

    add_amount = int(input("Enter income:\n"))

    sql_command_temp_bal = """SELECT balance FROM card WHERE number = ?;"""
    cur.execute(sql_command_temp_bal, (card_number,))
    temp_balance = cur.fetchall()[0][0]
    temp_balance = temp_balance + add_amount
    conn.commit()

    sql_command_new_bal = """UPDATE card SET balance = ? WHERE number = ?;"""
    cur.execute(sql_command_new_bal, (temp_balance, card_number))
    conn.commit()

    print("Income was added!")
    logged_in(card_number)


def close_account(card_number):

    sql_command_close = """DELETE FROM card WHERE number = ?;"""
    cur.execute(sql_command_close, (card_number,))
    conn.commit()
    print("\n\nThe account has been closed!")


def main():

    global exit_

    while exit_ == "off":

        option = int(input("1. Create an account:\n2. Log into account:\n0. Exit:\n"))

        if option == 1:
            # create new card number
            new_card()

        elif option == 2:
            # ask card / pin info
            login_check()

        else:
            # exit
            exit_ = "on"

    else:
        print("\n\nBye!")


main()
conn.close()

