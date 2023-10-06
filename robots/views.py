from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from openpyxl import Workbook
from datetime import datetime, timedelta
import json

from helpers.helpers import validate_json_data
from .signals import robot_created
from .forms import RobotForm
from .models import Robot

# Create your views here.


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

                robot_created.send(Robot, robot=robot)
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


@method_decorator(csrf_exempt, name="dispatch")
def generate_weekly_report(request):
    wb = Workbook()

    end_date = datetime.now()  # Current datetime
    start_date = end_date - timedelta(days=7)  # 7 days before current datetime
    unique_models = Robot.objects.values_list("model", flat=True).distinct()
    for model in unique_models:
        ws = wb.create_sheet(title=model)

        ws["A1"] = "Модель"
        ws["B1"] = "Версия"
        ws["C1"] = "Количество за неделю"

        model_version_data = (
            Robot.objects.filter(model=model)
            .filter(created__range=(start_date, end_date))
            .values("model", "version")
            .annotate(count_for_week=Count("version"))
            .order_by("model", "version")
        )

        for i, data in enumerate(
            model_version_data, start=2
        ):  # Start from row 2, assuming headers in row 1
            ws.cell(row=i, column=1, value=data["model"])
            ws.cell(row=i, column=2, value=data["version"])
            ws.cell(row=i, column=3, value=data["count_for_week"])
    default_sheet = wb["Sheet"]
    wb.remove(default_sheet)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response[
        "Content-Disposition"
    ] = f"attachment; filename=report {start_date.date()}_{end_date.date()}.xlsx"

    # Save the workbook to the response content
    wb.save(response)

    return response
