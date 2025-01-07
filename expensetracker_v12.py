# CMSC 127 PROJECT: Expense Tracker Using mariadb and Python
# Date Created: 2023-06-04
# Authors: ST1L - Group 3
    # Brinas, Sheila Mycah D.
    # Cabanisas, Joanna Mae P.
    # Sagun, Justin Carl C.
# -----------------------------------------------------------------------------------------
# Importing the modules
import mariadb
import sys
import re  # re for regex, checking string patterns
from tabulate import tabulate  # for printing the tables
from datetime import date
import datetime

# Variables
host = "localhost"
user = "root"
password = "root"  # enter your root password here
database = "expensetracker"

# Connecting to the database
try:
    print("Establishing connection with", database, "database...")
    db1 = mariadb.connect(host=host, user=user, password=password, database=database)
    db1.autocommit = True
    command_handler = db1.cursor()
except Exception as e:
    print(e)
    print("\nERROR: Failed to connect to", database, "database.")

# Application Header
header = """------------------------------------------------------\n 		   EXPENSE TRACKER\n------------------------------------------------------"""
print(header)

# -----------------------------------------------------------------------------------------
# Functions for "Managing Friends"

# Fetching all data from the user table
command_handler.execute("SELECT * FROM user")
users = command_handler.fetchall()

# Function for adding a friend to the user's friends listS
def addFriend():
    print("\nADDING A FRIEND\n--------------------------------------")
    first_name = input("Enter first name: ")
    middle_init = input("Enter middle initial: ")
    last_name = input("Enter last name: ")
    query = "INSERT INTO user (first_name, middle_init, last_name) VALUES(%s, %s, %s)"
    query_vals = (first_name, middle_init, last_name)
    command_handler.execute(query, query_vals)
    db1.commit()
    print("\nSTATUS: Friend added successfully.")
    command_handler.execute("SELECT * FROM user")  # update the users list locally in the code
    global users
    users = command_handler.fetchall()

# Function for removing a friend from the user's friends list
def removeFriend():
    try:
        command_handler.execute("SELECT * FROM user")
        null_checker = command_handler.fetchall()
        if len(null_checker) != 0:
            viewFriends()
            print("REMOVING A FRIEND\n--------------------------------------")
            uid = input("Enter user ID: ")

            while True:
                try:
                    uid = int(uid)
                    break
                except ValueError:
                    uid = input("\nPlease enter a valid user ID: ")
            
            qchecker = ("SELECT * FROM user WHERE user_id = %d")
            qchecker_vals = (uid,)
            command_handler.execute(qchecker, qchecker_vals)
            user = command_handler.fetchall()
            if(user[0][0] == 1):
                print("\nERROR: You can't delete your own data.")
                return

            if len(user) == 0:
                print("\nERROR: Friend does not exist. Please try again.")
            else:
                uid_to_delete = user[0][0]
                if(user[0][4] > 0 or user[0][5] > 0):
                    print("Unable to remove user who is involved with an expense")
                    return
                try:
                    command_handler.execute("SELECT * FROM user_group WHERE user_id = %d", (uid_to_delete,))
                    groups_of_user = command_handler.fetchall()
                except mariadb.Error as e:
                    print(e)
                query = "DELETE FROM user WHERE user_id = %d"
                query_vals = (uid,)
                command_handler.execute(query, query_vals)
                print("\nSTATUS: Friend deleted successfully.")
                if len(groups_of_user) != 0:
                    for g in groups_of_user:
                        try:
                            command_handler.execute("SELECT * FROM egroup WHERE group_id = %d", (g[0],))
                            groups = command_handler.fetchall()
                        except mariadb.Error as e:
                            print(e)
                        new_num = groups[0][2]-1 # reduce the num_of_members of the group by 1
                        update_query = "UPDATE egroup SET num_of_members = %d WHERE group_id = %d"
                        update_query_vals = (new_num, g[0])
                        command_handler.execute(update_query, update_query_vals)
                        print(f"Successfully updated group {g[0]}")
        else:
            print("\nERROR: You do not have any friends yet.")
    except:
        print("\nERROR: Friend does not exist. Please try again.")

# Function for searching a friend from the user's friends list
def searchFriend():
    try:
        command_handler.execute("SELECT * FROM user")
        null_checker = command_handler.fetchall()
        if len(null_checker) != 0:
            print("\nSEARCHING A FRIEND\n--------------------------------------")
            uid = input("Enter user ID: ")

            while True:
                try:
                    uid = int(uid)
                    break
                except ValueError:
                    uid = input("\nPlease enter a valid user ID: ")
            
            if(uid==1):
                print("\nERROR: Friend does not exist. Please try again.")
            else:
                qchecker = ("SELECT * FROM user WHERE user_id = %d")
                qchecker_vals = (uid,)
                command_handler.execute(qchecker, qchecker_vals)
                user = command_handler.fetchall()
                if len(user) != 0:
                    print("\n------------------------------------------------------------------------")
                    print("                             SEARCH RESULTS                                      ")
                    print("------------------------------------------------------------------------")
                    print(tabulate(user, ["User ID", "First Name", "MI", "Last Name", "Amount Owed", "Amount Lent"]))
                    print("------------------------------------------------------------------------")
                else:
                    print("\nERROR: Friend does not exist. Please try again.")
        else:
            print("\nERROR: You do not have any friends yet.")
    except:
        print("\nERROR: Friend does not exist. Please try again.")

# Function for updating a friend's information
def updateFriend():
    try:
        command_handler.execute("SELECT * FROM user")
        null_checker = command_handler.fetchall()
        if len(null_checker) != 0:
            viewFriends()
            print("\nUPDATING A FRIEND\n--------------------------------------")
            uid = input("Enter user ID: ")
            while True:
                try:
                    uid = int(uid)
                    break
                except ValueError:
                    uid = input("\nPlease enter a valid user ID.")
            if(uid==1):
                print("\nERROR: Friend does not exist. Please try again.")
            else:
                qchecker = ("SELECT * FROM user WHERE user_id = %d")
                qchecker_vals = (uid,)
                command_handler.execute(qchecker, qchecker_vals)
                user = command_handler.fetchall()

                if len(user) == 0:
                    print("\nERROR: Friend does not exist. Please try again.")
                else:
                    updateType = friendUpdateOptions()
                    if (updateType) == 1:
                        new_fn = input("Enter new first name: ")
                        query = "UPDATE user SET first_name=%s WHERE user_id = %d"
                        query_vals = (new_fn, uid)
                        command_handler.execute(query, query_vals)
                        print("\nSTATUS: Friend's first name has been updated.")
                    elif (updateType) == 2:
                        new_mi = input("Enter new middle initial: ")
                        query = "UPDATE user SET middle_init=%s WHERE user_id = %ds"
                        query_vals = (new_mi, uid)
                        command_handler.execute(query, query_vals)
                        print("\nSTATUS: Friend's middle initial has been updated.")
                    elif (updateType) == 3:
                        new_ln = input("Enter new last name: ")
                        query = "UPDATE user SET last_name=%s WHERE user_id = %d"
                        query_vals = (new_ln, uid)
                        command_handler.execute(query, query_vals)
                        print("\nSTATUS: Friend's last name has been updated.")
                    else:
                        print("\nERROR: Invalid input! Please try again.")
        else:
            print("\nERROR: You do not have any friends yet.")
    except:
        print("\nERROR: Friend does not exist. Please try again.")


# Additional function for viewing all friends
def viewFriends():
    command_handler.execute("SELECT * FROM user WHERE user_id!=1")
    users = command_handler.fetchall()
    if len(users) == 0:
        print("\nERROR: You do not have any friends yet.")
    else:
        print("\n------------------------------------------------------------------------")
        print("                              FRIENDS LIST                                      ")
        print("------------------------------------------------------------------------")
        print(tabulate(users, ["User ID", "First Name", "MI", "Last Name", "Amount Owed", "Amount Lent"]))
        print("------------------------------------------------------------------------")
    
# -----------------------------------------------------------------------------------------
# Functions for "Managing Groups"

# Fetching all data from the egroup table
command_handler.execute("SELECT * FROM egroup")
egroups = command_handler.fetchall()

# Function for adding a group
def addGroup():
    print("\nCREATING A GROUP\n--------------------------------------")
    group_name = input("Enter group name: ")
    while True:  # validator group name
        if len(group_name) > 30:
            print("\nSTATUS: Group name invalid. Please try a shorter one.")
            group_name = input("\nEnter new group name: ")
        else:
            break
    num_of_members = 1
    query = "INSERT INTO egroup (group_name, num_of_members) VALUES (%s, %d)"
    query_vals = (group_name, num_of_members)
    command_handler.execute(query, query_vals)
    command_handler.execute("SELECT * FROM egroup")
    global egroups
    egroups = command_handler.fetchall()
    gid = egroups[len(egroups)-1][0]
    # db1.commit()
    print("\nSTATUS: Group created successfully.") # group created in the database already
    query = "INSERT INTO user_group (user_id, group_id) VALUES (%d, %d)"
    query_vals = (1, gid)
    command_handler.execute(query, query_vals)

    choice = input("Would you like to add members to this group now? (y/n): ")
    while True:
        if choice == 'y': #if the user wants to add members, ask who
            viewFriends()
            members_string = input("Enter the User IDs of the members separated by commas: ")
            while True:
                try:
                    members = [] #actual list that will contain the user IDs of members
                    members_list = members_string.split(',')
                    for i in range(len(members_list)):
                        for j in range(len(users)):
                            if(int(members_list[i]) == 1):
                                print("\nERROR: You are already a part of this group.")
                                break
                            elif(int(members_list[i]) == users[j][0]):
                                members.append(users[j][0])
                            else:
                                continue
                    if(len(members)>len(users)):
                        print("\nERROR: Too many users or some users don't exist")
                        return
                    # members have the group IDs now
                    # insert into table user_group repeatedly
                    for j in range(len(members)):
                        query = "INSERT INTO user_group (user_id, group_id) VALUES (%d, %d)"
                        query_vals = (members[j], gid)
                        command_handler.execute(query, query_vals)
                    query = "UPDATE egroup SET num_of_members=%d WHERE group_id = %d"
                    query_vals = (len(members)+1, gid)
                    command_handler.execute(query, query_vals)
                    print(f"\nSTATUS: Successfully created group with {len(members)+1} members.")
                    break
                except ValueError:
                    members_string = input("Enter new User IDs seperated by commas: ")
            break
            
        elif choice == 'n':
            print("\nSTATUS: Group created with only you as a member.")
            break
        else:
            choice = input("Would you like to add members to this group now? (y/n): ")

# Function for deleting a group
def removeGroup():
    try:
        command_handler.execute("SELECT * FROM egroup")
        null_checker = command_handler.fetchall()
        if len(null_checker) != 0:
            viewGroup()
            print("REMOVING A GROUP\n--------------------------------------")
            gid = input("Enter group ID: ")

            while True:
                try:
                    gid = int(gid)
                    break
                except ValueError:
                    gid = input("Please enter a valid Group ID")

            qchecker = ("DELETE FROM egroup WHERE group_id = %d")
            qchecker_vals = (gid,)
            command_handler.execute(qchecker, qchecker_vals)
            print("\nSTATUS: Group deleted successfully.")
        else:
            print("\nERROR: You do not have any groups yet.")
    except mariadb.Error as e:
        print(f"{e}")
        print("\nERROR: Group does not exist. Please try again.")

# Function for searching a group
def searchGroup():
    try:
        command_handler.execute("SELECT * FROM egroup")
        null_checker = command_handler.fetchall()
        if len(null_checker) != 0:
            print("\nSEARCHING A GROUP\n--------------------------------------")
            gid = input("Enter group ID: ")

            while True:
                try:
                    gid = int(gid)
                    break
                except ValueError:
                    gid = input("\nPlease enter a valid Group ID: ")
            
            qchecker = ("SELECT * FROM egroup WHERE group_id = %d")
            qchecker_vals = (gid,)
            command_handler.execute(qchecker, qchecker_vals)
            egroups = command_handler.fetchall()
            if len(egroups) != 0:
                header = """---------------------------------------------\n 		  GROUP DETAILS\n---------------------------------------------"""
                print(header)
                print(tabulate(egroups, ["Group ID", "Group Name", "Number of Members"]))
                print("---------------------------------------------\n")
            else:
                print("\nERROR: Group does not exist. Please try again.")
        else:
            print("\nERROR: You do not have any groups yet.")
    except:
        print("\nERROR: Group does not exist. Please try again.")

# Function for updating a group's information
def updateGroup():
    try:
        command_handler.execute("SELECT * FROM egroup")
        null_checker = command_handler.fetchall()
        if len(null_checker) != 0:
            print("\nUPDATING A GROUP\n--------------------------------------")
            gid = input("Enter group ID: ")

            while True:
                try:
                    gid = int(gid)
                    break
                except ValueError:
                    gid = input("\nPlease enter a valid Group ID: ")
            
            qchecker = ("SELECT * FROM egroup WHERE group_id = %d")
            qchecker_vals = (gid,)
            command_handler.execute(qchecker, qchecker_vals)
            egroups = command_handler.fetchall() #egroups is the tuple with the matching group name and num of members

            if len(egroups) == 0:
                print("\nERROR: Group does not exist. Please try again.")
            else:
                updateType = groupUpdateOptions()
                command_handler.execute("SELECT * FROM user_group WHERE group_id = %d", (egroups[0][0],))
                users_group = command_handler.fetchall() #get rows from user_group that has this group number
                if (updateType) == 1: #edit group name
                    new_gn = input("Enter new group name: ")
                    query = "UPDATE egroup SET group_name=%s WHERE group_id = %d"
                    query_vals = (new_gn, gid)
                    command_handler.execute(query, query_vals)
                    print("\nSTATUS: Group's name has been updated.")
                elif (updateType) == 2: # add members
                    new_nm = input("Enter how many members do you want to add: ")
                    viewFriends()
                    members_string = input("Enter User IDs separated by commas: ")
                    members_string = members_string.split(',') # becomes a list of numbers
                    try:
                        for m in range(len(members_string)):
                            for n in users_group: #check first if the new member is already in the group
                                if(int(members_string[m]) == n[1]): #if they are, remove them from the string list
                                    print(f"{n[1]} is already a member of this group")
                                    members_string.pop(m)
                    except:
                        pass
                    new_nm = len(members_string) #renew the num of added members in case some were removed
                    for i in range(new_nm): #insert the final list of members in the database
                        try:
                            query = "INSERT INTO user_group (user_id, group_id) VALUES (%d, %d)"
                            query_vals = (int(members_string[i]), egroups[0][0])
                            command_handler.execute(query, query_vals)
                            print(f"Successfull added {members_string[i]} to {egroups[0][0]}")
                        except mariadb.Error as e:
                            print(e)
                    query = "UPDATE egroup SET num_of_members=%d WHERE group_id=%d"
                    query_vals = (new_nm+egroups[0][2], gid)
                    command_handler.execute(query, query_vals)
                    print("\nSTATUS: Group's number of members has been updated.")
                elif (updateType) == 3: #remove members
                    print("in remove members")
                    members = [] # members will contain the data of the group members
                    for ug in users_group:
                        for u in users:
                            if(ug[1] == u[0]):
                                members.append(u)
                    # show members of the group
                    print("\n------------------------------------------------------------------------")
                    print("                            FRIENDS IN GROUP                                      ")
                    print("------------------------------------------------------------------------")
                    print(tabulate(members, ["User ID", "First Name", "MI", "Last Name", "Amount Owed", "Amount Lent"]))
                    print("------------------------------------------------------------------------")

                    # remove the member
                    while True:
                        try:
                            to_remove = input("Enter User ID of the member to be removed: ")
                            to_remove = int(to_remove)
                            if(to_remove == 1):
                                print("You can't remove yourself from a group")
                                return
                            for m in members:
                                if(to_remove == m[0]):
                                    query = "DELETE FROM user_group WHERE group_id = %d AND user_id = %d"
                                    query_vals = (users_group[0][0], to_remove)
                                    command_handler.execute(query, query_vals)
                                    print(f"Successfully deleted user {to_remove} from {users_group[0][0]}")
                                    query = "UPDATE egroup SET num_of_members=%d WHERE group_id = %d"
                                    query_vals = ((egroups[0][2] - 1), gid)
                                    command_handler.execute(query, query_vals)
                                    print("Group's number of members has been updated.")
                            break
                        except:
                            print("\nERROR: Invalid user ID.")
        else:
            print("\nERROR: You do not have any groups yet.")
    except:
        print("\nERROR: Group does not exist. Please try again.")

# Function for viewing all groups
def viewGroup():
    command_handler.execute("SELECT * FROM egroup")
    egroups = command_handler.fetchall()
    if len(egroups) == 0:
        print("\nERROR: You do not have any groups yet.")
    else:
        print("\n---------------------------------------------")
        print("                 GROUPS LIST                   ")
        print("---------------------------------------------")
        print(tabulate(egroups, ["Group ID", "Group Name", "Number of Members"]))
        print("---------------------------------------------\n")

# -----------------------------------------------------------------------------------------
# Functions for "Managing Expenses"

# Fetching all data from the user table
command_handler.execute("SELECT * FROM expense")
expenses = command_handler.fetchall()

#view all expenses, even those that were settled
def viewExpenses():
    command_handler.execute("SELECT * FROM expense")
    expenses = command_handler.fetchall()
    if len(expenses) == 0:
        print("\nERROR: You do not have any expenses yet.")
    else:
        print("\n-----------------------------------------------------------------------------")
        print("                                EXPENSE LIST                      ")
        print("-----------------------------------------------------------------------------")
        print(tabulate(expenses, ["Expense ID", "Description", "Type", "Amount", "Payee", "Date", "Remaining Balance", "Settled"]))
        print("-----------------------------------------------------------------------------\n")

# Function for adding an expense
def addExpense():
    with_friend = 0
    in_group = False
    gid = 0
    command_handler.execute("SELECT * FROM user")
    users = command_handler.fetchall()
    print("\nADDING AN EXPENSE\n--------------------------------------")
    description = input("Enter a description of the expense: ")
    while True:  # validator for description
        if len(description) > 30:
            print("Last entered value was invalid")
            description = input("Enter new description of the expense: ")
        else:
            break

    expense_type = input("Type of Expense (Group or Friend): ")
    while True:  # validator for type of expense
        if expense_type.lower() not in ['group', 'friend']:
            print("Last entered value was invalid")
            expense_type = input("Enter type of expense (Individual, Group, or Friend): ")
        else:
            if(expense_type.lower() == 'group'):
                in_group = True
            break

    amount = input("Enter amount: ")
    while True: # validator for amount
        try: #try to typecast amount into float
            amount = float(amount)
            dec_places = str(amount)[::-1].find(".")
            if(dec_places > 2): #if amount can become a flaot, check if decimal places is greater than 2
                print("Please only use up to two decimal places")
                amount = input("Enter new amount: ")
            else:
                break
        except ValueError: #if amount cant become float, re-enter amount
            print("Invalid amount, please enter numbers")
            amount = input("Enter amount: ")
    if(in_group):
        print("expense is with group, ask which group is the expense with")
        viewGroup()
        gid = input("Enter group ID of group with this expense: ")
        while True:
            try:
                gid = int(gid)
                #show members of this group
                command_handler.execute("SELECT * FROM user_group WHERE group_id = %d", (gid,))
                user_group = command_handler.fetchall()
                members = []
                for ug in user_group:
                    for u in users:
                        if(ug[1] == u[0]):
                            members.append(u)
                
                # show members of the group
                    print("\n------------------------------------------------------------------------")
                    print("                            FRIENDS IN GROUP                                      ")
                    print("------------------------------------------------------------------------")
                    print(tabulate(members, ["User ID", "First Name", "MI", "Last Name", "Amount Owed", "Amount Lent"]))
                    print("------------------------------------------------------------------------")
                
                # ask for the payee's user ID
                uid = input("Enter payee's User ID: ")
                while True:
                    try:
                        uid = int(uid)
                        for m in members:
                            if(m[0] == uid):
                                #use this uid as payee
                                payee = uid
                        break
                    except ValueError:
                        uid = input("Enter valid user ID: ")
                break
            except ValueError:
                gid = input("Enter valid group ID of group with this expense: ")
    else:
        p_choice = input("Did you pay? (y/n): ")
        if(p_choice == 'y'):
            payee = 1
            viewFriends()
            with_friend = input("Enter friend's User ID: ")
            while True: # validator for payee
                try: #try to typecast payee into int
                    with_friend = int(with_friend)
                    valid_with_friend = False
                    for i in range(len(users)): # find payee in the users
                        if(int(users[i][0])) == with_friend and with_friend!=1:
                            valid_with_friend = True
                            break
                    if valid_with_friend:
                        break
                    else:
                        with_friend = input("Enter valid friend's User ID: ")
                except ValueError: #if amount cant become float, re-enter amount
                    print("Invalid amount, please enter numbers")
                    with_friend = input("Enter valid friend's User ID: ")
        else:
            viewFriends()
            payee = input("Enter payee's User ID: ")
            while True: # validator for payee
                try: #try to typecast payee into int
                    payee = int(payee)
                    valid_payee = False
                    for i in range(len(users)): # find payee in the users
                        if(int(users[i][0])) == payee and payee != 1:
                            valid_payee = True
                            break
                    if valid_payee:
                        break
                    else:
                        payee = input("Enter valid payee's User ID: ")
                except ValueError: #if amount cant become float, re-enter amount
                    print("Invalid amount, please enter numbers")
                    payee = input("Enter valid payee's User ID: ")

    dateformat = "%Y-%m-%d"
    date = input("Enter transaction date *YYYY-MM-DD*: ")
    while True:
        try:
            dateObject = datetime.datetime.strptime(date, dateformat)
            break;
            # print(dateObject)
        except:
            print("Incorrect date format")
            date = input("Enter transaction date *YYYY-MM-DD*: ")
    #insert into expense table
    query = "INSERT INTO expense (description, type, amount, payee, transaction_date) VALUES(%s, %s, %d, %s, %s)"
    query_vals = (description, expense_type, amount, payee, date)
    command_handler.execute(query, query_vals)
    print("\nSTATUS: Expense added successfully.")
    #get the id of the expense just made
    command_handler.execute("SELECT * FROM expense")
    expenses = command_handler.fetchall()
    eid = expenses[len(expenses)-1][0]
    #insert into has_expense table as well and update the user table for the money owed and lent
    if(in_group): #for group scenario
        query = "INSERT INTO has_expense (user_id, group_id, expense_id) VALUES(%d, %d, %d)"
        query_vals = (payee, gid, eid)
        command_handler.execute(query, query_vals)
        #logic for dividing money here
        #payee has 0 balance, but the total expense will be divided by the number of members in the group
        command_handler.execute("SELECT * FROM egroup WHERE group_id = %d", (gid,))
        group = command_handler.fetchall() #get group info here
        command_handler.execute("SELECT * FROM user_group WHERE group_id = %d", (gid,))
        members = command_handler.fetchall() #get all members of the group here
        amount_owed = amount/group[0][2] #group[0][2] is the number of members of the group
        amount_lent = amount-amount_owed
        command_handler.execute("UPDATE expense SET remaining_balance = %d WHERE expense_id = %d", (amount_lent, eid))
        #update the amount_lent of the payee
        for u in users:
            if u[0] == payee:
                new_amount_lent = amount_lent+float(u[5])
                query = "UPDATE user SET amount_lent=%d WHERE user_id=%d"
                query_vals = (new_amount_lent, payee)
                command_handler.execute(query, query_vals)
        # print(f"nagpautang na si {payee}")
        for i in range(group[0][2]):
            if(members[i][1] == payee):
                continue
            else:
                for u in users:
                    if(members[i][1] == u[0]):
                        new_amount_owed = amount_owed+float(u[4])
                        query = "UPDATE user SET amount_owed=%d WHERE user_id=%d"
                        query_vals = (new_amount_owed, members[i][1]) #update their amount owed using the original amount owed + new amount owed
                        command_handler.execute(query, query_vals)
                        # print(f"may utang na si {members[i][1]}")
                    else:
                        continue
    else: #for expesne with friend scenario
        amount_owed = amount/2
        #update the remaining balance of expense regardless who pays
        command_handler.execute("UPDATE expense SET remaining_balance = %d WHERE expense_id = %d", (amount_owed, eid))
        try:
            if payee == 1: #if user paid the expense
                query = "INSERT INTO has_expense (user_id, expense_id) VALUES(%d, %d)"
                query_vals = (with_friend, expenses[len(expenses)-1][0])
                command_handler.execute(query, query_vals)
                #update the user table
                for u in users:
                    if(u[0] == payee):
                        alt = amount_owed + float(u[5])
                        command_handler.execute("UPDATE user SET amount_lent=%d WHERE user_id=1", (alt,))
                    elif(u[0] == with_friend):
                        aod = amount_owed + float(u[4])
                        command_handler.execute("UPDATE user SET amount_owed=%d WHERE user_id=%d", (aod, with_friend))
            else: #if the friend paid the expense
                query = "INSERT INTO has_expense (user_id, expense_id) VALUES(%d, %d)"
                query_vals = (payee, expenses[len(expenses)-1][0])
                command_handler.execute(query, query_vals)
                for u in users:
                    if(u[0] == 1):
                        aod = amount_owed + float(u[4])
                        command_handler.execute("UPDATE user SET amount_owed=%d WHERE user_id=1", (aod,))
                    elif(u[0] == payee):
                        alt = amount_owed + float(u[5])
                        command_handler.execute("UPDATE user SET amount_lent=%d WHERE user_id=%d", (alt, payee))
        except mariadb.Error as e:
            print(e)

def deleteExpense():
    command_handler.execute("SELECT * FROM expense")
    expenses = command_handler.fetchall()
    if(len(expenses)==0):
        print("No expenses yet")
    else:
        viewExpenses()
        print("DELETING AN EXPENSE\n--------------------------------------")
        valid = False
        eid = input("Enter expense ID: ")
        while True: #validate expense ID to be deleted
            try:
                eid = int(eid)
                for e in expenses:
                    if e[0] == eid:
                        valid = True
                        expense = e
                if valid: break
                else: eid = input("Enter valid expense ID in the table: ")
            except ValueError:
                eid = input("Enter valid expense ID: ")
        amount = expense[3]
        payee = expense[4]
        #get the row in has_expense that involves this expense
        command_handler.execute("SELECT * FROM has_expense WHERE expense_id = %d", (eid,))
        has_expense = command_handler.fetchall()
        #get the list of users
        command_handler.execute("SELECT * FROM user")
        users = command_handler.fetchall()
        if(expense[2] == 'group'):
            #if the expense to be deleted is in a group
            #get group info
            command_handler.execute("SELECT * FROM egroup WHERE group_id = %d", (has_expense[0][1],))
            group = command_handler.fetchall()
            #get the members of the group
            command_handler.execute("SELECT * FROM user_group WHERE group_id = %d", (has_expense[0][1],))
            members = command_handler.fetchall()
            #remove money lent from payee, then remove money owed from groupmates
            amount_owed = amount/group[0][2]
            amount_lent = amount-(amount_owed)
            #exciting part!!
            for m in members:
                for u in users:
                    if(m[1] == u[0]): #this means that the user is a member of the group involved in the transaction
                        old_ao = float(u[4])
                        old_al = float(u[5])
                        # print(f"user {u[0]}'s old_ao:{old_ao} and old_al:{old_al}")
                        if(u[0] == payee): #this user is the payee, update their amount lent
                            # print(f"update payee's {u[0]} amount_lent")
                            new_al = old_al - float(amount_lent)
                            # print(old_al)
                            # print(new_al)
                            query = "UPDATE user SET amount_lent = %d WHERE user_id = %d"
                            query_vals = (new_al, u[0])
                            command_handler.execute(query, query_vals)
                        else: #this user is a grp member, update their amount owed
                            # print(f"update group member's {u[0]} amount owed")
                            new_ao = old_ao - float(amount_owed)
                            # print(new_ao)
                            # print(new_ao)
                            query = "UPDATE user SET amount_owed = %d WHERE user_id = %d"
                            query_vals = (new_ao, u[0])
                            command_handler.execute(query, query_vals)
            command_handler.execute("DELETE FROM expense WHERE expense_id=%d", (eid,))
            print("Successfully deleted expense")
        else:
            print("indiv")
            if(payee == has_expense[0][0]): #when payee is not the user
                # print("payee is not user")
                # print(payee)
                #update user table with the amount
                for u in users:
                    # print(u)
                    if(u[0] == payee):
                        #found payee (friend)
                        # print("found payee")
                        new_amount_lent = float(u[5]) - float(amount)/2
                        # print(new_amount_lent)
                        query = "UPDATE user SET amount_lent = %d WHERE user_id = %d"
                        query_vals = (new_amount_lent, u[0])
                        command_handler.execute(query, query_vals)
                    elif(u[0] == 1):
                        #found user
                        # print("found user")
                        new_amount_owed = float(u[4]) - float(amount)/2
                        # print(new_amount_owed)
                        query = "UPDATE user SET amount_owed = %d WHERE user_id = %d"
                        query_vals = (new_amount_owed, u[0])
                        command_handler.execute(query, query_vals)
                    else:
                        continue
            else:
                # print("user is payee")
                for u in users:
                    if(u[0] == payee):
                        #found payee (user)
                        # print("payee")
                        new_amount_lent = float(u[5]) - float(amount)/2
                        # print(new_amount_lent)
                        query = "UPDATE user SET amount_lent = %d WHERE user_id = %d"
                        query_vals = (new_amount_lent, u[0])
                        command_handler.execute(query, query_vals)
                    elif(u[0] == has_expense[0][0]):
                        #found user
                        # print("user")
                        new_amount_owed = float(u[4]) - float(amount)/2
                        # print(new_amount_owed)
                        query = "UPDATE user SET amount_owed = %d WHERE user_id = %d"
                        query_vals = (new_amount_owed, u[0])
                        command_handler.execute(query, query_vals)
                    else:
                        continue
            command_handler.execute("DELETE FROM expense WHERE expense_id=%d", (eid,))
            print("Successfully deleted expense")

def searchExpense():
    command_handler.execute("SELECT * FROM expense")
    expenses = command_handler.fetchall()
    if(len(expenses)==0):
        print("No expenses yet")
    else:
        eid = input("Enter expense ID to search expenses: ")
        try:
            expense = []
            for e in expenses:
                if e[0] == int(eid):
                    expense.append(e)
            print("\n-----------------------------------------------------------------------------")
            print("                                EXPENSE LIST                      ")
            print("-----------------------------------------------------------------------------")
            print(tabulate(expense, ["Expense ID", "Description", "Type", "Amount", "Payee", "Date", "Settled"]))
            print("-----------------------------------------------------------------------------\n")
        except ValueError:
            print("\nERROR: No expense with that ID.")

def updateExpense():
    command_handler.execute("SELECT * FROM expense")
    expenses = command_handler.fetchall()
    if(len(expenses)==0):
        print("No expenses yet.")
    else:
        viewExpenses()
        eid = input("Enter expense ID to update: ")
        try:
            for e in expenses:
                if e[0] == int(eid):
                    expense = e
        except ValueError:
            print("No expense with that ID")
        print(expense)
        #expense now holds the info of the expense to be updated
        while True:
            choice = updateExpenseOptions()
            if(choice == 1):
                settle(expense)
                break
            elif(choice == 2):
                editDate(expense)
            elif(choice == 3):
                editDescription(expense)
            elif(choice == 4):
                break
            else:
                print("Invalid choice")
    
def settle(expense):
    if expense[7] == 1:
        print("Expense already settled")
        return
    eid = expense[0]
    expense_type = expense[2]
    amount = float(expense[3])
    payee = expense[4]
    remaining_balance = float(expense[6])

    command_handler.execute("SELECT * FROM has_expense WHERE expense_id = %d", (eid,))
    has_expense = command_handler.fetchall() #get the involved group or friend in this expense

    if(expense_type == 'friend'):
        #settle expense with a friend
        command_handler.execute("SELECT * FROM user WHERE user_id = %d", (has_expense[0][0],))
        friend = command_handler.fetchall() #get friend's info
        command_handler.execute("SELECT * FROM user WHERE user_id = 1")
        user = command_handler.fetchall() #get user's info
        if(payee == 1): #when the user is the payee
            while True: # validator for pay
                try:
                    pay = float(input("How much will they pay?: "))
                    if pay > remaining_balance:
                        print("You're paying too much")
                    elif pay <= 0:
                        print("Can't pay less than 0")
                    else:
                        break
                except ValueError:
                    print("Invalid input")
            # Add transaction to payment table
            query = "INSERT INTO payment (user_id, expense_id, amount_paid) VALUES (%d, %d, %d)"
            query_vals = (friend[0][0], eid, pay)
            command_handler.execute(query, query_vals)
            # UPDATE user table to reflect payment
            new_amount_lent = float(user[0][5]) - pay
            new_amount_owed = float(friend[0][4]) - pay
            query = "UPDATE user SET amount_lent = %d WHERE user_id = 1" #update user
            query_vals = (new_amount_lent,)
            command_handler.execute(query, query_vals)
            query = "UPDATE user SET amount_owed = %d WHERE user_id = %d" #update friend
            query_vals = (new_amount_owed, friend[0][0])
            command_handler.execute(query, query_vals)
        else: # when the payee is another user
            while True: # validator for pay
                try:
                    pay = float(input("How much will you pay?: "))
                    if pay > remaining_balance:
                        print("You're paying too much")
                    elif pay <= 0:
                        print("Can't pay less than 0")
                    else:
                        break
                except ValueError:
                    print("Invalid input")
            # Add transaction to payment table
            query = "INSERT INTO payment (user_id, expense_id, amount_paid) VALUES (%d, %d, %d)"
            query_vals = (friend[0][0], eid, pay)
            command_handler.execute(query, query_vals)
            # UPDATE user table to reflect payment
            new_amount_lent = float(friend[0][5]) - pay
            new_amount_owed = float(user[0][4]) - pay
            query = "UPDATE user SET amount_owed = %d WHERE user_id = 1" #update user
            query_vals = (new_amount_owed,)
            command_handler.execute(query, query_vals)
            query = "UPDATE user SET amount_lent = %d WHERE user_id = %d" #update friend
            query_vals = (new_amount_lent, friend[0][0])
            command_handler.execute(query, query_vals)
        #get first the updated tuple from the table if successful in updating payment and user table
        command_handler.execute("SELECT * FROM expense WHERE expense_id = %d", (eid,))
        expense = command_handler.fetchall()
        remaining_balance = float(expense[0][6])
        # UPDATE remaining balance of expense
        new_balance = remaining_balance-pay
        query = "UPDATE expense SET remaining_balance = %d WHERE expense_id = %d"
        query_vals = (new_balance, eid)
        command_handler.execute(query, query_vals)

        # update is_settled if new balance is 0
        # if new_balance == 0:
        #     command_handler.execute("UPDATE expense SET is_settled = 1 WHERE expense_id = %d", (eid,))

    else: #when the expense_type is group
        #get the group members of this expense
        command_handler.execute("SELECT * FROM has_expense WHERE expense_id = %d", (eid,))
        has_expense = command_handler.fetchall()
        gid = has_expense[0][1]
        #need group info num of members for validation
        command_handler.execute("SELECT * FROM egroup WHERE group_id = %d", (gid,))
        group = command_handler.fetchall()
        command_handler.execute("SELECT u.user_id, u.first_name, u.middle_init, u.last_name, u.amount_owed, u.amount_lent FROM user u, user_group ug WHERE u.user_id = ug.user_id AND group_id = %d", (gid,))
        members = command_handler.fetchall()
        aod = amount/(group[0][2])
        print(aod)
        while True: #this will validate the uid of the one who will pay
            try:
                print("\n------------------------------------------------------------------------")
                print("                            FRIENDS IN GROUP                                      ")
                print("------------------------------------------------------------------------")
                print(tabulate(members, ["User ID", "First Name", "MI", "Last Name", "Amount Owed", "Amount Lent"]))
                print("------------------------------------------------------------------------")
                payer = int(input("Enter User ID of the one who wil settle their payment: "))
                flag = False
                for m in members:
                    if payer == m[0] and payer != payee:
                        #get the payment table to keep track if this group members is fully paid
                        command_handler.execute("SELECT * FROM payment WHERE user_id = %d AND group_id = %d AND expense_id = %d", (payer, gid, eid))
                        payments = command_handler.fetchall()
                        sump = 0
                        for p in payments:
                            sump += p[4]
                        left = aod - sump
                        if left == 0:
                            print("This person is already fully paid")
                        else:
                            flag = True
                if flag:
                    break
                else:
                    print("ERROR: Make sure entered user is not the payee or is a member of the group")
            except ValueError:
                print("Invalid input")
        while True:
            try:
                pay = float(input("How much will {person} pay?: ".format(person = "you" if payer == 1 else "they")))
                if pay > aod:
                    print("You're paying too much")
                elif pay <= 0:
                    print("Can't pay less than 0")
                else:
                    break
            except ValueError:
                print("Invalid input")
        print("valid pay")
        #add transaction to payment table
        query = "INSERT INTO payment (user_id, group_id, expense_id, amount_paid) VALUES(%d, %d, %d, %d)"
        query_vals = (payer, gid, eid, pay)
        command_handler.execute(query, query_vals)
        # get the most recent remaining balance for checking later
        command_handler.execute("SELECT * FROM expense WHERE expense_id = %d", (eid,))
        expense = command_handler.fetchall()
        #update user table
        for m in members:
            if m[0] == payer:
                new_amount_owed = float(m[4])-pay
                command_handler.execute("UPDATE user SET amount_owed = %d WHERE user_id = %d", (new_amount_owed, payer))
            elif m[0] == payee:
                new_amount_lent = float(m[5])-pay
                command_handler.execute("UPDATE user SET amount_lent = %d WHERE user_id = %d", (new_amount_lent, payee))
            else:
                continue
        # UPDATE remaining balance of expense
        new_balance = remaining_balance-pay
        query = "UPDATE expense SET remaining_balance = %d WHERE expense_id = %d"
        query_vals = (new_balance, eid)
        command_handler.execute(query, query_vals)

    # update is_settled if new balance is 0
    if new_balance == 0:
        command_handler.execute("UPDATE expense SET is_settled = 1 WHERE expense_id = %d", (eid,))
        print("This expense is now settled")

    

def editDate(expense):
    print("\nUPDATING EXPENSE TRANSACTION DATE\n--------------------------------------")
    dateformat = "%Y-%m-%d"
    date = input("Enter new transaction date *YYYY-MM-DD*: ")
    while True:
        try:
            dateObject = datetime.datetime.strptime(date, dateformat)
            break;
        except:
            print("Incorrect date format.")
            date = input("Enter new transaction date *YYYY-MM-DD*: ")
    query = "UPDATE expense SET transaction_date = %s WHERE expense_id = %d"
    query_vals = (date, expense[0])
    command_handler.execute(query, query_vals)
    print("\nSuccessfully edited transaction date of this expense.")

def editDescription(expense):
    print("\nUPDATING EXPENSE DESCRIPTION\n--------------------------------------")
    new_desc = input("Enter new description for this expense: ")
    try:
        query = "UPDATE expense SET description = %s WHERE expense_id = %d"
        query_vals = (new_desc, expense[0])
        command_handler.execute(query, query_vals)
        print("\nSuccessfully edited description of this expense.")
    except ValueError:
        print("Unable to set new description.")

def viewReports():
    print("\nVIEWING REPORTS\n--------------------------------------")
    while True:
        try:
            repOpt = reportOptions()
            if(repOpt == 1):
                monthExpense()
            elif(repOpt == 2):
                friendExpense()
            elif(repOpt == 3):
                groupExpense()
            elif(repOpt == 4):
                currBalance()
            elif(repOpt == 5):
                friendswithBalance()
            elif(repOpt == 6):
                groupswithBalance()
            elif(repOpt == 7):
                break
            else: print("\nERROR: Invalid input! Please try again.")
        except ValueError:
            print("\nERROR: Invalid input! Please try again.")

# -----------------------------------------------------------------------------------------
# Reports

# View all expenses made within a month
def monthExpense():
    try:
        command_handler.execute("SELECT * FROM expense")
        null_checker = command_handler.fetchall()
        if (len(null_checker) != 0):
            emonth = input("Enter month (January-December): ")
            
            while True:
                try:
                    emonth = str(emonth)
                    break
                except ValueError:
                    emonth = input("Please enter a valid month): ")
                    
            query = "SELECT * FROM expense WHERE MONTHNAME(transaction_date) = %s"
            query_vals = (emonth,)
            command_handler.execute(query, query_vals)
            monthexpenses = command_handler.fetchall()
            if(len(monthexpenses) != 0):
                    print("\nVIEWING EXPENSES FOR THE MONTH:", emonth )
                    print("\n-----------------------------------------------------------------------------")
                    print("                                EXPENSE LIST                      ")
                    print("-----------------------------------------------------------------------------")
                    print(tabulate(monthexpenses, ["Expense ID", "Description", "Type", "Amount", "Payee", "Date", "Settled"]))
                    print("-----------------------------------------------------------------------------\n")
            else: print("No expenses yet.")
        else: print("No expenses yet.")
    except mariadb.Error as e:
        print(f"{e}")
        print("Please try again.")
        
# View all expenses made with a friend
def friendExpense():
    command_handler.execute("SELECT * FROM expense")
    expenses = command_handler.fetchall()
    if(len(expenses)==0):
        print("No expenses yet.")
    else:
        command_handler.execute("SELECT * FROM expense WHERE type = 'Friend'")
        friendexpenses = command_handler.fetchall()
        if(len(friendexpenses)==0):
            print("You have no expenses made with a friend.")
        else:
            print("\nVIEWING EXPENSES MADE WITH A FRIEND")
            print("\n-----------------------------------------------------------------------------")
            print("                                EXPENSE LIST                      ")
            print("-----------------------------------------------------------------------------")
            print(tabulate(friendexpenses, ["Expense ID", "Description", "Type", "Amount", "Payee", "Date", "Settled"]))
            print("-----------------------------------------------------------------------------\n")

# View all expenses made with a group
def groupExpense():
    command_handler.execute("SELECT * FROM expense")
    expenses = command_handler.fetchall()
    if(len(expenses)==0):
        print("No expenses yet.")
    else:
        command_handler.execute("SELECT * FROM expense WHERE type = 'Group'")
        groupexpenses = command_handler.fetchall()
        if(len(groupexpenses)==0):
            print("You have no group expenses yet.")
        else:
            print("\nVIEWING GROUP EXPENSES")
            print("\n--------------------------------------------------------------------------------------------------")
            print("                                EXPENSE LIST                      ")
            print("--------------------------------------------------------------------------------------------------")
            print(tabulate(groupexpenses, ["Expense ID", "Description", "Type", "Amount", "Payee", "Date", "Remaining Balance", "Settled"]))
            print("--------------------------------------------------------------------------------------------------\n")

# View current balance from all expenses
def currBalance():
    command_handler.execute("SELECT SUM(amount_owed) FROM user WHERE user_id = 1")
    userBal = command_handler.fetchone()
    print("\n---------------------------------------------")
    print("                ACCOUNT                      ")
    print("---------------------------------------------")
    for b in userBal:
        print("Your current balance is:", float(b))
    print("---------------------------------------------\n")

# View all friends with outstanding balance
def friendswithBalance():
    command_handler.execute("SELECT * FROM user")
    users = command_handler.fetchall()
    if(len(users)==1):
        print("\nERROR: You do not have any friends yet.")
    else:
        command_handler.execute("SELECT user_id, first_name, last_name, SUM(amount_owed) FROM user WHERE user_id!=1 GROUP BY user_id HAVING SUM(amount_owed)>0")
        friendsBal = command_handler.fetchall()
        if(len(friendsBal)==0):
            print("\nYou do not have friends with outstanding balance.")
        else:
            print("\n-----------------------------------------------------")
            print("           FRIENDS WITH OUTSTANDING BALANCE              ")
            print("-----------------------------------------------------")
            print(tabulate(friendsBal, ["User ID", "First Name", "Last Name", "Total Balance"]))
            print("-----------------------------------------------------\n")

# View all groups with an outstanding balance
def groupswithBalance(): 
    command_handler.execute("SELECT * FROM egroup")
    groups = command_handler.fetchall()
    if(len(groups)==0):
        print("\nERROR: You do not have any groups yet.")
    else:
        command_handler.execute("SELECT g.group_id, g.group_name, g.num_of_members, SUM(e.remaining_balance) FROM egroup g NATURAL JOIN has_expense h NATURAL JOIN expense e WHERE e.is_settled=0 GROUP BY group_id HAVING SUM(e.remaining_balance)>0")
        groupsBal = command_handler.fetchall()
        if(len(groupsBal)==0):
            print("\nYou do not have groups with outstanding balance.")
        else:
            print("\n--------------------------------------------------------------")
            print("           GROUPS WITH OUTSTANDING BALANCE              ")
            print("--------------------------------------------------------------")
            print(tabulate(groupsBal, ["Group ID", "Group Name", "Number of Members", "Total Balance"]))
            print("--------------------------------------------------------------\n")

# -----------------------------------------------------------------------------------------
# Menu Options
def mainMenu():
    menu = """
		     MAIN MENU
		-------------------
        [1] Manage Friends
        [2] Manage Groups
        [3] Manage Expenses
        [4] View Reports
        [5] Exit
	"""
    print(menu)
    choice = int(input("Enter choice: "))
    return choice


def expenseOptions(): 
    expOpt = """
		   MANAGE EXPENSES
		---------------------
		[1] Add an Expense
		[2] Delete an Expense
		[3] Search an Expense
		[4] Update an Expense
		[5] View All Expenses
		[6] Back to Main Menu
	"""
    print(expOpt)
    choice = int(input("Enter choice: "))
    return choice

def updateExpenseOptions():
    expOpt = """
		   MANAGE EXPENSES
		---------------------
		[1] Settle Expense
		[2] Edit Expense Transaction Date
		[3] Edit Expense Description
		[4] Return to Manage Expenses
	"""
    print(expOpt)
    choice = int(input("Enter choice: "))
    return choice

def friendOptions():
    friendOpt = """
		   MANAGE FRIENDS
		-------------------
		[1] Add a Friend
		[2] Remove a Friend
		[3] Search a Friend
		[4] Update a Friend
		[5] View All Friends
		[6] Back to Main Menu
	"""
    print(friendOpt)
    choice = int(input("Enter choice: "))
    return choice


def friendUpdateOptions():
    friendUpdateOpt = """
		   UPDATE FRIEND
		-------------------
		[1] Update First Name
		[2] Update Middle Initial
		[3] Update Last Name
	"""
    print(friendUpdateOpt)
    choice = int(input("Enter choice: "))
    return choice


def groupOptions():
    groupOpt = """
		   MANAGE GROUPS
		------------------
		[1] Create a Group
		[2] Delete a Group
		[3] Search a Group
		[4] Update a Group
		[5] View All Groups
		[6] Back to Main Menu
	"""
    print(groupOpt)
    choice = int(input("Enter choice: "))
    return choice

def groupUpdateOptions():
    groupUpdateOpt = """
		   UPDATE GROUP
		-------------------
                [1] Update Group Name
                [2] Add Member
                [3] Remove Member
	"""
    print(groupUpdateOpt)
    choice = int(input("Enter choice: "))
    return choice

def reportOptions():
    menu = """
		            REPORTS
	-------------------------------------
            [1] Expenses for the Month
            [2] Expenses With a Friend
            [3] Group Expenses
            [4] Current Balance
            [5] Friends with Outstanding Balance
            [6] Groups with Outstanding Balance
            [7] Back to Main Menu
	"""
    print(menu)
    choice = int(input("Enter choice: "))
    return choice

# Main Program
if __name__ == "__main__":
    while True:
        optionSelected = mainMenu()
        if optionSelected == 1:  # manage friends
            while True:
                try:
                    friendOptSelected = friendOptions()
                    if friendOptSelected == 1:  # add a friend
                        addFriend()
                    elif friendOptSelected == 2:  # remove a friend
                        removeFriend()
                    elif friendOptSelected == 3:  # search a friend
                        searchFriend()
                    elif friendOptSelected == 4:  # update a friend
                        updateFriend()
                    elif friendOptSelected == 5:  # view all friends
                        viewFriends()
                    elif friendOptSelected == 6:  # back to main menu
                        break
                    else:
                        print("\nERROR: Invalid input! Please try again.")
                except:
                    print("\nERROR: Invalid input! Please try again.")
        elif optionSelected == 2:  # manage groups
            while True:
                try:
                    groupOptSelected = groupOptions()
                    if groupOptSelected == 1:  # add a group
                        addGroup()
                    elif groupOptSelected == 2:  # remove a group
                        removeGroup()
                    elif groupOptSelected == 3:  # search a group
                        searchGroup()
                    elif groupOptSelected == 4:  # update a group
                        updateGroup()
                    elif groupOptSelected == 5:  # view all groups
                        viewGroup()
                    elif groupOptSelected == 6:  # back to main menu
                        break
                    else:
                        print("\nERROR: Invalid input! Please try again.")
                except:
                    print("\nERROR: Invalid input! Please try again.")
        elif optionSelected == 3:  # manage expenses
            while True:
                try:
                    expenseOptSelected = expenseOptions()
                    if expenseOptSelected == 1:
                        addExpense()
                    elif expenseOptSelected == 2:
                        deleteExpense()
                    elif expenseOptSelected == 3:
                        searchExpense()
                    elif expenseOptSelected == 4:
                        updateExpense()
                    elif expenseOptSelected == 5:
                        viewExpenses()
                    elif expenseOptSelected == 6:
                        break
                except ValueError as e:
                    print(e)
                    print("\nERROR: Invalid input! Please try again.")
        elif optionSelected == 4: # view reports
            viewReports()
        elif optionSelected == 5:  # exit 
            print("\nUntil next time. Bye!\n")
            break 
            sys.exit(1)
        else:
            print("\nERROR: Invalid input! Please try again.")

# PROJECT TRACKER: Pacheck nalang if oks na yung feature or if may error pa, panote nalang sa tapat non. ty!
# Features:
# Manage Expenses
# Add           /
# Delete        /
# Search        /
# Update

# Manage Friends - working naman lahat sakin tho if may time pa, i think pwede pa i-optimize yung ibang ganaps
# Add			/
# Delete		/
# Search		/
# Update		/

# Manage Groups - working naman lahat tho di aq sure if tama ba na hingin pa rin num of members of magderive na lang don
# Add			/
# Delete		/
# Search		/
# Update		/

# Reports:
# 		View all expenses made within a month
# 	/	View all expenses made with a friend
# 	/	View all expenses made with a group
# 	/	View current balance from all expenses
# 	/	View all friends with outstanding balance
# 	/	View all groups
# 	/	View all groups with an outstanding balance
