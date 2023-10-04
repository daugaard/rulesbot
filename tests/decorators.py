import logging
import warnings


def prevent_request_warnings(original_function):
    """
    If we need to test for 404s or 405s this decorator can prevent the
    request class from throwing warnings.
    """

    def new_function(*args, **kwargs):
        # raise logging level to ERROR
        logger = logging.getLogger("django.request")
        previous_logging_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

        # trigger original function that would throw warning
        original_function(*args, **kwargs)

        # lower logging level back to previous
        logger.setLevel(previous_logging_level)

    return new_function


def prevent_warnings(orignal_function):
    """
    Here we ignore python warnings for the original function.
    """

    def new_function(*args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            orignal_function(*args, **kwargs)

    return new_function
