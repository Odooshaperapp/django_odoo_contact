import json
import logging
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import ContactForm

logger = logging.getLogger(__name__)

def contact_view(request):
    """Handles the contact form submission and sends data to Odoo."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Prepare data for Odoo
                data = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "name": form.cleaned_data["name"],
                        "email": form.cleaned_data["email"],
                        "phone": form.cleaned_data["phone"],
                        "message": form.cleaned_data["message"],
                    }
                }

                # Set up headers
                headers = {
                    'Content-Type': 'application/json',
                }

                # Log outgoing request
                logger.info(f"Sending data to Odoo: {json.dumps(data)}")

                # Print for debugging
                print(f"Sending request to: {settings.ODOO_API_URL}")
                print(f"Request data: {json.dumps(data, indent=2)}")

                # Make request to Odoo
                response = requests.post(
                    settings.ODOO_API_URL,
                    json=data,
                    headers=headers,
                    verify=False  # Only for development
                )

                # Print response for debugging
                print(f"Response status: {response.status_code}")
                print(f"Response content: {response.text}")

                # Log response
                logger.info(f"Odoo Response Status: {response.status_code}")
                logger.info(f"Odoo Response Content: {response.text}")

                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        result = response_data.get('result', {})
                        if result.get('success'):
                            messages.success(request, "Your message has been sent successfully!")
                            form = ContactForm()  # Reset form
                        else:
                            error_msg = result.get('error', 'Unknown error')
                            messages.error(request, f"Error: {error_msg}")
                    except json.JSONDecodeError:
                        messages.error(request, "Invalid response from server")
                else:
                    messages.error(request, f"Server error: {response.status_code}")

            except requests.exceptions.ConnectionError:
                messages.error(request, "Could not connect to Odoo server. Please check if it's running.")
            except Exception as e:
                logger.exception("Unexpected error")
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = ContactForm()

    return render(request, "contact/contact_form.html", {"form": form})