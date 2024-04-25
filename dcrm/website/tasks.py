# tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Record


@shared_task
def send_login_email(user_email, username):
        user_email = user_email.strip()
        timestamp = timezone.now()
        subject = 'Login Successful'
        message = f'Hi {username},\n You just logged in to Easy Handover!\n'
        message += f'Time: {timestamp}\n'
        from_email = 'no-reply@amerestates.com'
        recipient_list = [user_email]
        send_mail(subject, message, from_email, recipient_list)
        


@shared_task
def send_register_email(email, username):
        user_email = user_email.strip()
        timestamp = timezone.now()
        subject = 'Registration Successful'
        message = f'Hi {username},\n You are succefully registered to Easy Handover!\n'
        from_email = 'no-reply@amerestates.com'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)
        
        
        
    
    

@shared_task
def send_contract_expiry_reminder():
    # Query the database for records with contracts about to expire
    records_to_remind = Record.objects.filter(contract_end__gte=timezone.now(), reminder_sent=False)

    for record in records_to_remind:
        # Calculate days until contract expiry
        days_until_expiry = (record.contract_end - timezone.now().date()).days

        # Check if it's time to send a reminder (e.g., 100 days before expiry)
        if days_until_expiry == 100:
            # Send a contract expiry reminder email
            send_mail_contract_expiry(record.user.email, record.user.username, days_until_expiry)

            # Update the record to mark the reminder as sent
            record.reminder_sent = True
            record.save()

# Helper function to send contract expiry reminder email
def send_mail_contract_expiry(user_email, username, days_until_expiry):
    subject = 'Contract Expiry Reminder'
    message = f'Hi {username},\n Your contract will expire in {days_until_expiry} days.\n Please take necessary actions.'
    from_email = 'no-reply@amerestates.com'
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)