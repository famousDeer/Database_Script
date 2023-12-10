# Recruitement Task

## Information
The script allows operations in the database with predefined commands. Each of them, except the `create_databse` command, requires a login and password. Some commands require administrator privileges. Login can be your email or telephone number.

## Create Database
This action does not require login and password. It takes data from `data/` directory and create `users.db`. Script accept `xml`, `csv` and `json` files.
```
├── data
│   └── YOUR DATA HERE
├── main.py
├── utils
│   └── utils.py
├── test
│   └── test.py
└── README.md
```

- Command: `python3 main.py create_database`
- It will print information what were done

## Admin Actions
This actions are for admin role.
- **Print total number of all valid accounts**
    - Command: `python3 main.py print-all-accounts --login <login> --password <password>`
    - It will print total number of users
    - Example: 

        >python3 main.py print-all-accounts --login '123456789' --password '12ass$#s'
        23

