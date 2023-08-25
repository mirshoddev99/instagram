import re
import threading
import phonenumbers
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
from decouple import config
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from twilio.rest import Client

from users.models import User

# Make a regular expression
# for validating an Email and Phone
email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
phone_regex = re.compile(r"^\+\d{1,3}[-\s]?\d{1,14}$")
username_regex = re.compile(r"^[a-zA-Z0-9_.-]+$")


def check_email_or_phone(email_or_phone):
    if re.fullmatch(email_regex, email_or_phone):
        email_or_phone = "email"
    elif phonenumbers.is_valid_number(phonenumbers.parse(email_or_phone)):
        email_or_phone = "phone"
    elif re.fullmatch(phone_regex, email_or_phone):
        email_or_phone = "phone"
    else:
        email_or_phone = "failed"
    return email_or_phone


def check_user_input_type(user_input):
    if re.fullmatch(email_regex, user_input):
        user_input = "email"
    elif re.fullmatch(username_regex, user_input):
        user_input = "username"
    elif re.fullmatch(phone_regex, user_input):
        user_input = "phone"
    else:
        user_input = "failed"
    return user_input


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']]
        )
        if data.get('content_type') == 'html':
            email.content_subtype = 'html'
        EmailThread(email).start()


def send_email(email, code):
    html_content = render_to_string(
        "email/activate_account.html",
        {"code": code}
    )
    data = {
        "subject": "Registration",
        "from": "oripovmirshod9@gmail.com",
        "to_email": email,
        "body": html_content,
        "content_type": "html"
    }
    Email.send_email(data=data)


def send_phone_number(name, phone_number, code):
    account_sid = config('account_sid')
    auth_token = config('auth_token')
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"Hello {name}! This is your verification code -> {code}",
        from_="+821058101928",
        to=phone_number
    )


def get_user(**kwargs):
    user = User.objects.filter(**kwargs)
    if not user:
        raise ValidationError(
            {
                "message": "Not Found"
            }
        )
    return user.first()


class CustomPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            "previous": self.get_previous_link(),
            "next": self.get_next_link(),
            "count": self.page.paginator.count,
            "results": data
        })
