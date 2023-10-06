from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import OrderForm
from .models import Order
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
