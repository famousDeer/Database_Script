# Recruitement Task
- Created by: Dawid Trzciński
- Email: dawidtrzcinski1@gmail.com

## Environment
In `env/` directory is `conda_environment.yml` file, that gives you every information about packages and python version were use for this project. Command below create conda environment:
```bash
    >conda env create -f conda_environment.yml
```

## General Information
The script allows operations in the database with predefined commands. Each of them, except the `create_databse` command, requires a login and password. Some commands require administrator privileges. Login can be your email or telephone number.

## Create Database
This action does not require login and password. It takes data from `data/` directory and create `users.db`. Script accept `xml`, `csv` and `json` files.
```
├── data
│   └── YOUR DATA HERE
├── env
│   └── conda_environment.yml
├── utils
│   └── utils.py
├── .gitignore
├── README.md
└── main.py
```

- Command: `python3 main.py create_database`
- It will print information what were done
- **IMPORTANT** It will only create database base on data files in directory it won't update any information that exists.

## Admin Actions
This actions are for admin role **ONLY**.
- **Print total number of all valid accounts**
    - Command: `python3 main.py print-all-accounts --login <login> --password <password>`
    - It will print total number of users
    - Example: 
    ```bash
        >python3 main.py print-all-accounts --login '123456789' --password '12ass$#s'
        23
    ```
- **Print the oldest existing account**
    - Command: `python3 main.py print-oldest-account --login <login> --password <password>`
    - It will print name, email and date of creation of the oldest account
    - Example:
    ```bash
        >python3 main.py print-oldest-account --login '123456789' --password '12sdf#@'
        name: Adam
        email_address: Adam@test.com
        created_at: 2001-01-23 14:14:14
    ```
- **Print grouped children by age**
    - Command: `python3 main.py group-by-age --login <login> --password <password>`
    - It will print grouped children by age and how many children are in specific age in ascending order
    - Example:
    ```bash
        >python3 main.py group-by-age --login '123456789' --password '123sdf#@$'
        age: 10, count: 5
        age: 5,  count: 6
        age: 12, count: 10
    ```

## User Actions
This actions are for admin and user role.
- **Print user children**
    - Command: `python3 main.py print-children --login <login> --password <password>`
    - It will print user children
    - Example:
    ```bash
        >python3 main.py print-children --login '123456789' --password '123AF#@D'
        Adam, 10
        Steve, 12
    ```
- **Find users with children of same age**
    - Command: `python3 main.py find-similar-children-by-age --login <login> --password <password>`
    - It will print user name, telephone number and children. Base on user children age will find at least one in other users children.
    - Example:
    ```bash
        >python3 main.py find-similar-children-by-age --login '123456789' --password '12wxd#@'
        Adam, 738467290: Steve, 10; Olive 12
        John, 182934267: Adam, 2; Bart 9
    ```



