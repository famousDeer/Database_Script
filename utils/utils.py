import os
import xml.etree.ElementTree as ET
import json
import sqlite3
import pandas as pd

from typing import List



class CreateDatabase:
    def __init__(self, database: str = "users.db", path: str = "data/") -> None:
        self.database = database
        self.path = path
        self.data_list = list()    
        self.path_list = {}

    def find_data_paths(self) -> None:
        xml_list = list()
        csv_list = list()
        json_list = list()
        for root, dirs, files in os.walk(self.path):
            for f in files:
                if f.endswith(".xml"):
                    xml_list.append(os.path.relpath(os.path.join(root, f), "."))
                elif f.endswith(".csv"):
                    csv_list.append(os.path.relpath(os.path.join(root, f), "."))
                elif f.endswith(".json"):
                    json_list.append(os.path.relpath(os.path.join(root, f), "."))
        self.path_list = {"json": json_list, "xml": xml_list, "csv": csv_list}
    
    def is_valid_email(self, email: str) -> bool:
        local_part, domain_part, *_ = email.split("@")
        dot_part = domain_part.split(".")

        # Checking email contains only one "@" symbol
        if _ != []:
            return False

        # Checking if local part contain at least 1 character
        if local_part == '':
            return False

        # Checking if part between "@" and "." have at least 1 character
        if dot_part[0] == '':
            return False

        # Checking if last part is alphanumeric and properly length
        if len(dot_part[1]) < 1 or len(dot_part[1]) > 4 or not dot_part[1].isalnum():
            return False

        return True
    
    def create_users_table(self) -> None:
        with sqlite3.connect(self.database) as connect:
            
            cursor = connect.cursor()
            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS users
                           ([user_id] INTEGER PRIMARY KEY, 
                            [firstname] TEXT,
                            [telephone_number] TEXT, 
                            [email] TEXT, 
                            [password] TEXT, 
                            [role] TEXT, 
                            [created_at] TIMESTAMP, 
                            [children] BOOLEAN
                            )""")
            connect.commit()
        print(f"[INFO] Users table create in {self.database}")
    
    def create_child_table(self) -> None:
        with sqlite3.connect(self.database) as connect:
            
            cursor = connect.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS childs
                            ([child_id] INTEGER PRIMARY KEY, 
                            [child_name] TEXT,
                            [child_age] INTEGER, 
                            [user_id] INTEGER,
                            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE)
                           """)
            connect.commit()
        print(f"[INFO] Child table create in {self.database}")

    def delete_duplicate(self) -> None:
        with sqlite3.connect(self.database) as connect:
            
            cursor = connect.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("""
                           DELETE FROM users WHERE user_id NOT IN 
                           (SELECT MIN(user_id) FROM users GROUP BY telephone_number) 
                           OR user_id NOT IN 
                           (SELECT MIN(user_id) FROM users GROUP BY email)
                           """)
            connect.commit()

    def json_files(self) -> None:
        for json_path in self.path_list['json']:
            with open(json_path, 'r') as f:
                users_JSON = json.load(f)
            for user_JSON in users_JSON:
                self.data_list.append(user_JSON)

    def xml_files(self) -> None:
        for xml_path in self.path_list['xml']:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for user_element in root.findall('.//user'):
                firstname = user_element.find('firstname').text
                telephone_number = user_element.find('telephone_number').text
                email = user_element.find('email').text
                password = user_element.find('password').text
                role = user_element.find('role').text
                created_at = user_element.find('created_at').text
                children = user_element.find('children')
                children_data = []
                if children is not None:
                    for child_elem in children.findall('child'):
                        child_name = child_elem.find('name').text
                        child_age = child_elem.find('age').text
                        children_data.append({'name': child_name, 'age': child_age})
                
                user_data = {
                            'firstname': firstname,
                            'telephone_number': telephone_number,
                            'email': email,
                            'password': password,
                            'role': role,
                            'created_at': created_at,
                            'children': children_data
                            }
                self.data_list.append(user_data) 
    
    def csv_files(self) -> None:
        for csv_path in self.path_list['csv']:
            df = pd.read_csv(csv_path, delimiter=';', keep_default_na=False )
            df_dict = df.to_dict('records')
            for idx, record in enumerate(df_dict):
                if record["children"] != '':
                    children_list = record["children"].split(',')
                    new_children_list = list()
                    for children in children_list:
                        child_name, child_age = children.split(' ')
                        new_children_list.append({
                            "name": child_name,
                            "age": ''.join(filter(str.isdigit, child_age))
                        })
                    df_dict[idx]["children"] = new_children_list
                self.data_list.append(df_dict[idx])




    def insert_data(self) -> None:
        with sqlite3.connect(self.database) as connect:
            
            cursor = connect.cursor()
            table_exists = cursor.execute("""
                            SELECT COUNT(firstname) 
                            FROM users""").fetchone()[0]
            if table_exists > 1:
                idx = table_exists + 1
            else:
                idx = 0
            for data in self.data_list:
                if data["telephone_number"] != '' and self.is_valid_email(data["email"]) == True:
                    query_parent = """
                                    INSERT INTO users (firstname, telephone_number, email, password, role, created_at, children)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                   """
                    query_child = """
                                    INSERT INTO childs (child_name, child_age, user_id)
                                    VALUES (?, ?, ?)
                                  """


                    valid_phone_number = "".join(data["telephone_number"].split())
                    data["telephone_number"] = valid_phone_number[len(valid_phone_number)-9:]

                    if data["children"] != []:
                        children_found = True
                    else:
                        children_found = False

                    values_parents = (
                        data["firstname"],
                        data["telephone_number"],
                        data["email"],
                        data["password"],
                        data["role"],
                        data["created_at"],
                        children_found,
                    )
                    cursor.execute(query_parent, values_parents)
                    idx += 1
                    if children_found:
                        for child in data["children"]:
                            values_childs = (
                                child["name"],
                                child["age"],
                                idx,
                            )
                            cursor.execute(query_child, values_childs)
            connect.commit()

class AccountManager:
    def __init__(self, command: str, login: str, password: str, database: str = "users.db") -> None:
        self.command = command
        self.login = login
        self.password = password
        self.database = database
        self.commands = ["create_database", 
                         "print-all-accounts", 
                         "print-oldest-account",
                         "group-by-age",
                         "print-children",
                         "find-similar-children-by-age"]
        self.login_type = ''
        
    def check_available_command(self) -> None:
        if self.command not in self.commands:
            print(f"[ERROR] Uknown command \n[INFO] Available commands: {', '.join(self.commands)}")
            return None
        else:
            return self.command

    def check_login_password(self) -> str:
        with sqlite3.connect(self.database) as connect:
            cursor = connect.cursor()
            if '@' in self.login:
                query = """
                        SELECT role
                        FROM users
                        WHERE email = ? AND password = ?"""
                self.login_type = 'email'
            else:
                query = """
                        SELECT role
                        FROM users
                        WHERE telephone_number = ? AND password = ?"""
                self.login_type = 'telephone_number' 
            role = cursor.execute(query, (self.login, self.password)).fetchone()[0]
            if role == '':
                print("[Warning] You don't have any role in your record")
                return None
        return role
    
    def print_all_accounts(self) -> None:
        with sqlite3.connect(self.database) as connect:
            cursor = connect.cursor()
            count = cursor.execute("""
                                   SELECT COUNT(user_id) 
                                   FROM users""").fetchone()
        print(count[0])

    def print_oldest_account(self) -> None:
        with sqlite3.connect(self.database) as connect:
            cursor = connect.cursor()
            data = cursor.execute("""SELECT firstname, email, created_at 
                                     FROM users 
                                     ORDER BY created_at""").fetchall()[0]
        print(f"name: {data[0]}\nemail_address: {data[1]}\ncreated_at: {data[2]}")

    def group_by_age(self) -> None:
        with sqlite3.connect(self.database) as connect:
            cursor = connect.cursor()
            datas = cursor.execute("""
                                    SELECT child_age, COUNT(*) as counted_children
                                    FROM childs
                                    GROUP BY child_age
                                    ORDER BY counted_children ASC""").fetchall()
        for data in datas:
            print(f"age: {data[0]:<2}, count: {data[1]}")

    def print_children(self) -> List:
        with sqlite3.connect(self.database) as connect:
            cursor = connect.cursor()
            query = f"""
                    SELECT c.child_name, c.child_age
                    FROM users u
                    JOIN childs c ON u.user_id = c.user_id
                    WHERE u.{self.login_type} = ? AND u.password = ?
                    ORDER BY c.child_name ASC""" 
            children = cursor.execute(query, (self.login, self.password)).fetchall()
        if children == []:
            print("[INFO] You don't have any children in record")
        return children
    
    def find_similar_children_by_age(self) -> None:
        # Get children ages 
        children = self.print_children()

        with sqlite3.connect(self.database) as connect:
            cursor = connect.cursor()
            child_ages = [age for _, age in children]
            placeholder = ", ".join('?' for _ in child_ages)
            query = f"""
                    SELECT u.firstname, u.telephone_number, c.child_name, c.child_age
                    FROM users u
                    JOIN childs c ON u.user_id = c.user_id
                    WHERE c.child_age IN ({placeholder})
                    ORDER BY u.firstname, c.child_name ASC"""
            data = cursor.execute(query, child_ages).fetchall()

            # Prepare data for printing
            result_dict = {}
            for row in data:
                
                # Using (firstname, telephone_number) as the key
                user_key = (row[0], row[1])
                if user_key not in result_dict:
                    result_dict[user_key] = []

                # Adding (child_name, child_age) to the list
                result_dict[user_key].append((row[2], row[3]))  

            # Format the results as strings
            formatted_results = []
            for user, children in result_dict.items():
                user_str = f"{user[0]}, {user[1]}: "
                children_str = '; '.join([f"{child[0]}, {child[1]}" for child in children])
                formatted_results.append(user_str + children_str)

        for result in formatted_results:
            print(result)
            
