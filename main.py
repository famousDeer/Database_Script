import argparse

from utils.utils import CreateDatabase, AccountManager

def main():
    parser = argparse.ArgumentParser(description="Users database operations")
    parser.add_argument("command", help="Provide one of the following command: create_database, print-all-accounts, print-oldest-account, group-by-age, print-children, find-similar-children-by-age")
    parser.add_argument("--login", type=str, help="Provide your login, can be <email> or <telephone_number>")
    parser.add_argument("--password", type=str, help="Provide your password")

    args = parser.parse_args()
    manager = AccountManager(args.command, args.login, args.password)
    command = manager.check_available_command()
    
    # Login and password are not required to create database
    if args.login is not None or args.password is not None:
        role = manager.check_login_password()
        if role is None:
            return
    else:    
        if command == "create_database":
            db = CreateDatabase()
            db.find_data_paths()
            db.json_files()
            db.xml_files()
            db.csv_files()
            db.create_users_table()
            db.create_child_table()
            db.insert_data()
            db.delete_duplicate()
            return
        else: 
            print("[INFO] User not found")
            return
    
    if command is None:
        return
    
    elif command == "print-all-accounts":
        if role == "admin":
            manager.print_all_accounts()
        else:
            print("[INFO] Don't have permissions")

    elif command == "print-oldest-account":
        if role == "admin":
            manager.print_oldest_account()
        else:
            print("[INFO] Don't have permissions")

    elif command == "group-by-age":
        if role == "admin":
            manager.group_by_age()
        else:
            print("[INFO] Don't have permissions")

    elif command == "print-children":
        children = manager.print_children()
        for child in children:
            print(f"{child[0]}, {child[1]}")

    elif command == "find-similar-children-by-age":
        manager.find_similar_children_by_age()
   





if __name__ == "__main__":
    main()