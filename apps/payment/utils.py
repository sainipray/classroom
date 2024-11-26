from decimal import Decimal

from django.conf import settings


def final_price_with_other_expenses_and_gst(original_price, discounted_price=None, gst_percentage=None):
    # Define other fees (these could be defined in settings or calculated)
    internet_charges = getattr(settings, 'INTERNET_CHARGES', Decimal('10.00'))  # Example fixed internet charges
    platform_fees = getattr(settings, 'PLATFORM_FEE', Decimal('10.00'))  # Example fixed platform fee
    # Calculate GST
    if not gst_percentage:
        gst_percentage = getattr(settings, 'GST_PERCENTAGE', Decimal('18.0'))  # Define GST_PERCENTAGE in settings.py
    if discounted_price:
        gst_amount = (Decimal(discounted_price) + internet_charges + platform_fees) * Decimal(gst_percentage) / Decimal(
            '100')
        total_amount = Decimal(discounted_price) + gst_amount + internet_charges + platform_fees
    else:
        gst_amount = (Decimal(original_price) + internet_charges + platform_fees) * Decimal(gst_percentage) / Decimal(
            '100')
        total_amount = Decimal(original_price) + gst_amount + internet_charges + platform_fees
    data = {
        "original_price": Decimal(original_price),
        "gst_percentage": gst_percentage,
        "gst_amount": gst_amount.quantize(Decimal('0.01')),
        "internet_charges": internet_charges,
        "platform_fees": platform_fees,
        "total_amount": total_amount.quantize(Decimal('0.01'))
    }
    return data
