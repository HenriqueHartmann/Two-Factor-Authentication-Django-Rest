# Two-Factor-API

API developed with djangorestframework to registering new users and sending activation emails.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies needed.

Create a new virtual environment:
```
python3.8 -m venv venv
```

Activate virtualenv (OBS: on Linux):
```
source venv/bin/activate
```

Install all dependencies from requirements.txt:
```
pip install -r requirements.txt
```

## Settings

Copy the content of .env.example and paste on .env:
```
cp backend/core/.env.example backend/core/.env
```

Inside .env file, we already have some default values set. Then you can change to your taste:

![mail-env](https://raw.githubusercontent.com/HenriqueHartmann/Images/main/pictures/mail-env.png)

## Running

Apply the migrations:
```
backend/manage.py migrate
```

Run the server:
```
backend/manage.py runserver
```

## Endpoints

#### /api/register/

Body:
```
{
    "email": "some_email",
    "password": "some_passoword",
    "full_name": "some_name"
}
```
<hr>

#### /api/login/

Body:
```
{
    "email": "some_email",
    "password": "some_passoword"
}
```
<hr>

#### /api/user/

Header:
```
Authorization: Token <generated on login>
```
<hr>

#### /api/logout/

Header:
```
Authorization: Token <generated on login>
```

