import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdown_to_html", is_safe=True)
def markdown_to_html(value):
    """
    Converts Markdown text to HTML.

    Args:
        value (str): The Markdown text to be converted.

    Returns:
        str: The HTML representation of the Markdown text.
    """
    return mark_safe(markdown.markdown(value))
