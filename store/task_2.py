# tasks.py

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Property



@shared_task
def send_property_post_email(property_id):
    property = Property.objects.get(pk=property_id)
    subject = 'New Property Posted'

    # Render the email content from a template
    html_message = render_to_string('property_post_email_template.html', {'property': property})
    plain_message = strip_tags(html_message)  # Convert HTML to plain text

    from_email = 'dacretail2024@gmail.com'
    to_email = [property.user.email]

    send_mail(subject, plain_message, from_email, to_email, html_message=html_message)


@shared_task
def send_contact_verification_email(user_email, verification_code):
        subject = 'Verification Code for Sharing Contact Details'

        # Render the email content from a template
        html_message = render_to_string('contact_verification_email_template.html',
                                        {'verification_code': verification_code})
        plain_message = strip_tags(html_message)  # Convert HTML to plain text

        from_email = 'dacretail2024@gmail.com'  # Replace with your email
        to_email = [user_email]

        send_mail(subject, plain_message, from_email, to_email, html_message=html_message)


@shared_task
def send_contact_details_email(user_email, property_id):
    try:
        # Retrieve the Property object with the specified property_id
        property = Property.objects.get(pk=property_id)
        print(property)
        # Check if the property has a user associated with it
        if user_email:
            subject = 'Contact Details of Property Owner'
            # Render the email content from a template
            html_message = render_to_string('contact_details_email_template.html', {'property': property})
            plain_message = strip_tags(html_message)  # Convert HTML to plain text
            from_email = 'dacretail2024@gmail.com'  # Replace with your email
            to_email = [user_email]
            # Send the email
            send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
            # Log successful email sending
            print(f"Contact details email sent successfully to {to_email} for property ID {property_id}.")
        else:
            # Handle the case where the user email is not provided
            print(f"No user email provided for property ID {property_id}. Cannot send contact details email.")
    except ObjectDoesNotExist:
        # Handle the case where the specified property_id does not exist
        print(f"Property with ID {property_id} does not exist. Cannot send contact details email.")
    except Exception as e:
        # Handle any other exceptions that may occur during the email sending process
        print(f"An error occurred while sending contact details email for property ID {property_id}: {e}")

