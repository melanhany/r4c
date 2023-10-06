from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from robots.models import Robot
from orders.models import WaitlistedOrder
from robots.signals import robot_created


@receiver(robot_created)
def on_robot_created(sender, **kwargs):
    """
    Signal handler that sends an email notification to customers
    when a robot they were interested in becomes available in stock.

    Args:
        sender: The sender of the signal.
        kwargs (dict): Keyword arguments passed along with the signal.

    This signal handler performs the following actions:
    1. Retrieves the created robot from the signal arguments.
    2. Queries the WaitlistedOrder model for customers interested in this robot.
    3. Composes an email message with information about the available robot.
    4. Sends an email to the interested customers.

    Note: The email sending process uses Django's send_mail function.

    Exceptions:
        WaitlistedOrder.DoesNotExist: If no customers are interested in the robot, no action is taken.

    Example Usage:
    This signal handler is executed when a new robot is created and checks if any customers were
    interested in that robot. If interested customers exist, it sends them an email notification.
    """

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
