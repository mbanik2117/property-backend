# config/beat_schedule.py

from datetime import timedelta
from celery import shared_task
from django.apps import apps
from celery import Celery

# Make sure to set the default Django settings module for the 'celery' program.
from django.conf import settings

# This line is necessary to use Django models in the Celery tasks.
settings.configure()

from accounts.task_1 import send_signup_email, send_signup_verification, send_login_verification
from store.task_2 import send_property_post_email, send_contact_verification_email,send_contact_details_email


@shared_task
def schedule_send_signup_verification(user_id, verification_code):
    send_signup_verification.apply_async(args=[user_id, verification_code], countdown=5)  # Adjust countdown as needed


@shared_task
def schedule_send_signup_email(user_id):
    send_signup_email.apply_async(args=[user_id], countdown=5)  # Adjust countdown as needed


@shared_task
def schedule_send_login_verification(user_id, verification_code):
    send_login_verification.apply_async(args=[user_id, verification_code], countdown=5)


@shared_task
def schedule_send_property_post_email(property_id):
    send_property_post_email.apply_async(args=[property_id], countdown=5)


@shared_task
def schedule_send_contact_verification_email(user_email, verification_code):
    send_contact_verification_email.apply_async(args=[user_email, verification_code], countdown=5)  # Adjust countdown as needed

@shared_task
def schedule_send_contact_details_email(property_id):
    send_contact_details_email.apply_async(args=[property_id], countdown=5)  # Adjust countdown as needed


CELERY_BEAT_SCHEDULE = {
    'schedule-send-signup-verification': {
        'task': 'config.beat_schedule.schedule_send_signup_verification',
        'schedule': timedelta(minutes=1),  # Adjust the schedule as needed
        'options': {'expires': 60},  # Adjust the expiration time as needed
    },
    'schedule-send-signup-email': {
        'task': 'config.beat_schedule.schedule_send_signup_email',
        'schedule': timedelta(minutes=1),  # Adjust the schedule as needed
        'options': {'expires': 60},  # Adjust the expiration time as needed
    },

    'schedule-send-login-verification': {
        'task': 'config.beat_schedule.schedule_send_login_verification',
        'schedule': timedelta(minutes=1),
        'options': {'expires': 60},
    },
    'schedule-send-property-post-email': {
        'task': 'config.beat_schedule.schedule_send_property_post_email',
        'schedule': timedelta(minutes=1),  # Adjust the schedule as needed
        'options': {'expires': 60},  # Adjust the expiration time as needed
    },
    'schedule-send-contact-verification-email': {
        'task': 'config.beat_schedule.schedule_send_contact_verification_email',
        'schedule': timedelta(minutes=1),  # Adjust the schedule as needed
        'options': {'expires': 60},  # Adjust the expiration time as needed
    },
    'schedule-send-contact-details-email': {
        'task': 'config.beat_schedule.schedule_send_contact_details_email',
        'schedule': timedelta(minutes=1),  # Adjust the schedule as needed
        'options': {'expires': 60},  # Adjust the expiration time as needed
    },

}
