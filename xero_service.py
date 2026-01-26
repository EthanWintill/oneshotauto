import requests
import os
from token_manager import get_access_token

XERO_API_BASE = 'https://api.xero.com/api.xro/2.0'
XERO_TENANT_ID = os.environ.get('XERO_TENANT_ID')

def build_xero_quote_payload(quote):
    """Transform local Quote model to Xero Quote API format."""

    # Build line items from services
    line_items = []

    # Service name mapping
    service_names = {
        'chips': 'Paint Chips Repair',
        'scratches': 'Scratch Removal',
        'dents': 'Dent Repair',
        'headlights': 'Headlight Restoration',
        'wheels': 'Wheel Repair',
        'interior': 'Interior Detailing',
        'detail': 'Full Detail',
        'carspabasic': 'Car Spa Basic Package',
        'carspaplus': 'Car Spa Plus Package',
        'bed_liner': 'Bed Liner Installation',
        'paint_body': 'Paint & Body Work'
    }

    # Add each service as line items (if costs exist)
    for service_key, service_name in service_names.items():
        parts_cost = getattr(quote, f'{service_key}_parts_cost', 0) or 0
        labor_cost = getattr(quote, f'{service_key}_labor_cost', 0) or 0

        # Only add if service has costs
        if parts_cost > 0 or labor_cost > 0:
            # Add parts line item
            if parts_cost > 0:
                line_items.append({
                    'Description': f'{service_name} - Parts',
                    'Quantity': 1,
                    'UnitAmount': float(parts_cost)
                })

            # Add labor line item
            if labor_cost > 0:
                line_items.append({
                    'Description': f'{service_name} - Labor',
                    'Quantity': 1,
                    'UnitAmount': float(labor_cost)
                })

    # Build Xero quote payload
    payload = {
        'QuoteNumber': quote.quote_number,
        'Date': quote.date.strftime('%Y-%m-%d') if quote.date else None,
        'ExpiryDate': None,  # Optional: could calculate 30 days from date
        'Contact': {
            'ContactID': '65b6f228-c03a-4059-9272-d78b5f7f5322'
        },
        'LineItems': line_items,
        'Reference': f'{quote.year} {quote.make} {quote.model}',
        'Summary': f'Vehicle: {quote.year} {quote.make} {quote.model}\\nVIN: {quote.vin_number}',
        'Title': f'Body Work Quote - {quote.quote_number}',
        'Notes': quote.instructions if quote.instructions else ''
    }

    return payload

def send_quote_to_xero(quote):
    """Send quote to Xero Quotes API."""

    # Get access token (auto-refreshes if needed)
    access_token = get_access_token()
    if not access_token:
        return {
            'success': False,
            'error': 'Not connected to Xero. Please authorize first.'
        }

    # Build payload
    payload = build_xero_quote_payload(quote)

    # Make API call
    headers = {
        'Authorization': f'Bearer {access_token}',
        'xero-tenant-id': XERO_TENANT_ID,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    try:
        # POST to Xero Quotes endpoint
        response = requests.post(
            f'{XERO_API_BASE}/Quotes',
            json={'Quotes': [payload]},  # Xero expects array wrapper
            headers=headers
        )
        response.raise_for_status()

        result = response.json()

        return {
            'success': True,
            'data': result,
            'xero_quote_id': result.get('Quotes', [{}])[0].get('QuoteID'),
            'message': 'Quote successfully sent to Xero!'
        }

    except requests.exceptions.HTTPError as e:
        error_message = str(e)
        if e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get('Message', str(e))
            except:
                error_message = e.response.text

        return {
            'success': False,
            'error': error_message
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }
