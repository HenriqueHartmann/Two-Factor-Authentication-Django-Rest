from django.core.mail import EmailMessage
import random


class Util:

    @staticmethod
    def send_email(data):
        email = EmailMessage(to=[data['to_email']], subject=data['email_subject'], body=data['email_body'])
        email.send()

    @staticmethod
    def create_pin():
        pin = ""
        for i in range(6):
            pin += str(random.randint(0, 9))
        return pin
