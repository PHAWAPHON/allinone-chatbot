from http import HTTPStatus

from flask import jsonify


class AppException(Exception):

    code: int
    description: str


class MissingRequiredKey(AppException):

    code = HTTPStatus.BAD_REQUEST
    description = "Missing required key."


class InvalidSubjectID(AppException):

    code = HTTPStatus.NOT_FOUND
    description = "Not found subject match with the given id."


def exception_handler(e: AppException):
    return jsonify(
        {
            "message": e.description
        }
    ), e.code
