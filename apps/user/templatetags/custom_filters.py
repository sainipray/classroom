from django import template
from num2words import num2words

register = template.Library()


@register.filter
def inr_in_words(value):
    """
    Converts a number to Indian Rupee text.
    """
    try:
        value = float(value)  # Ensure it's a number
        rupee_text = num2words(value, lang='en_IN', to='currency', currency='INR')
        return rupee_text.capitalize()  # Capitalize the first letter
    except (ValueError, TypeError):
        return "Invalid number"
