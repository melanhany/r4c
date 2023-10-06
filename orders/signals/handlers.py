from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from robots.models import Robot
from orders.models import WaitlistedOrder
from robots.signals import robot_created


@receiver(robot_created)
def on_robot_created(sender, **kwargs):
    robot = kwargs["robot"]

    try:
        queryset = WaitlistedOrder.objects.filter(robot_serial=robot.serial)
        customers = [order.customer for order in queryset]
        waitlisted_robot = Robot.objects.filter(serial=robot.serial).first()
        subject = "Робот в наличии!"
        message = f"""Добрый день!
                     Недавно вы интересовались нашим роботом модели {waitlisted_robot.model}, версии {waitlisted_robot.version}. 
                     Этот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами"""
        from_email = "melanhany@gmail.com"
        recipients = [customer.email for customer in customers]
        send_mail(subject, message, from_email, recipients, fail_silently=False)

    except WaitlistedOrder.DoesNotExist:
        pass
