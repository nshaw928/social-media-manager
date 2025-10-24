from django.core.mail import send_mail
send_mail(
    'Test Email', 'This is a test.', 'nick@nicholasshaw.email',
    ['user@example.com'], fail_silently=False
)