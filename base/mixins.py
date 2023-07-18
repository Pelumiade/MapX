from django.contrib.contenttypes.models import ContentType

from rest_framework.exceptions import ValidationError

from mapx_app.models import ActivityLog
from base.constants import CREATED, MAPPED, SUCCESS, FAILED


class ActivityLogMixin:
    """Mixin to track user actions"""
    log_message = None

    def _get_action_type(self, request):
        print(request.data)
        action = request.data.get("action")
        print(action)
        if request.method.upper() == "POST":
            if action == CREATED:
                return CREATED
        elif request.method.upper() == 'PUT' or request.method.upper() == 'PATCH':
            return MAPPED

    def _build_log_message(self, request):
        return f"User: {self._get_user(request)} -- Action Type: {self._get_action_type(request)} -- Path: {request.path} -- Path Name: {request.resolver_match.url_name}"

    def get_log_message(self, request) -> str:
        return self.log_message or self._build_log_message(request)

    @staticmethod
    def _get_user(request):
        return request.user if request.user.is_authenticated else None

    def _write_log(self, request, response):
        status = SUCCESS if response.status_code < 400 else FAILED
        actor = self._get_user(request)

        data = {
            "actor": actor,
            "action_type": self._get_action_type(request),
            "status": status,

        }
        try:
            data["content_type"] = ContentType.objects.get_for_model(
                self.get_queryset().model
            )
            data["content_object"] = self.created_obj
            data["object_id"] = self.created_obj.id
        except (AttributeError, ValidationError):
            data["content_type"] = None
        except AssertionError:
            pass

        ActivityLog.objects.create(**data)

    def finalize_response(self, request, *args, **kwargs):
        response = super().finalize_response(request, *args, **kwargs)
        print(request)
        self._write_log(request, response)
        return response
