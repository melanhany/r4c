from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

from customers.models import Customer

from .forms import OrderForm
from .models import WaitlistedOrder
from robots.models import Robot
from helpers.helpers import validate_json_data

# Create your views here.


def create_order_instance(data) -> OrderForm:
    order_data = {"customer": data["customer"], "robot_serial": data["robot_serial"]}
    return OrderForm(order_data)


@method_decorator(csrf_exempt, name="dispatch")
def post_order(request) -> JsonResponse:
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            required_fields = {"customer", "robot_serial"}
            missing_fields = validate_json_data(data, required_fields)

            if missing_fields:
                missing_fields_list = ", ".join(missing_fields)
                response = {
                    "message": f"Missing required field(s) in JSON data: {missing_fields_list}"
                }
                return JsonResponse(response, status=400)

            form = create_order_instance(data)
            if form.is_valid():
                customer_id = data["customer"]
                robot_serial = data["robot_serial"]
                try:
                    Robot.objects.get(serial=robot_serial)
                except Robot.DoesNotExist:
                    customer = Customer.objects.get(id=customer_id)
                    waitlisted_order = WaitlistedOrder(
                        customer=customer, robot_serial=robot_serial
                    )
                    waitlisted_order.save()

                    response = {"message": "There isn't robots with such serial"}
                    return JsonResponse(response, status=400)

                order = form.save()
                response = {"message": f"New order added with id: {order.id}"}
                return JsonResponse(response, status=201)

            else:
                errors = form.errors
                response = {"message": "Validation error", "errors": errors}
                return JsonResponse(response, status=400)
        except json.JSONDecodeError:
            response = {"message": "Invalid JSON format in the request body."}
            return JsonResponse(response, status=400)
    else:
        response = {"message": "Invalid request."}
        return JsonResponse(response, status=400)
