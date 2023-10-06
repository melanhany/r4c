from typing import List
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json

from .forms import RobotForm
from .models import Robot

# Create your views here.


def validate_json_data(data, required_fields):
    missing_fields = required_fields - set(data.keys())
    return missing_fields


def create_robot_instance(data) -> RobotForm:
    robot_data = {
        "serial": "{}-{}".format(data["model"], data["version"]),
        "model": data["model"],
        "version": data["version"],
        "created": data["created"],
    }
    return RobotForm(robot_data)


@method_decorator(csrf_exempt, name="dispatch")
def post_robot(request) -> JsonResponse:
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            required_fields = {"model", "version", "created"}
            missing_fields = validate_json_data(data, required_fields)

            if missing_fields:
                missing_fields_list = ", ".join(missing_fields)
                response = {
                    "message": f"Missing required field(s) in JSON data: {missing_fields_list}"
                }
                return JsonResponse(response, status=400)

            form = create_robot_instance(data)
            if form.is_valid():
                robot = form.save()
                response = {"message": f"New robot added with id: {robot.id}"}
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

def generate_weekly_report():
    ...