import mimetypes
from os.path import basename
from urllib.parse import urlparse

import weasyprint
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.template.loader import render_to_string


def generate_pdf(template_name, context, output_filename="output.pdf", request=None, attachment=True):
    """
    Generate a PDF from a Django template and return as an HTTP response.

    :param template_name: Path to the Django template.
    :param context: Context data to render the template.
    :param output_filename: The filename for the generated PDF.
    :param request: Optional, request object for base URL resolution.
    :param attachment: Whether to send as an attachment or inline.
    :return: HttpResponse with the generated PDF.
    """

    def django_url_fetcher(url, timeout=10, ssl_context=None):
        if url.startswith('file:'):
            mime_type, encoding = mimetypes.guess_type(url)
            url_path = urlparse(url).path
            data = {'mime_type': mime_type, 'encoding': encoding, 'filename': basename(url_path)}

            if url_path.startswith(settings.MEDIA_URL):
                path = url_path.replace(settings.MEDIA_URL, settings.MEDIA_ROOT)
                data['file_obj'] = default_storage.open(path)
                return data

            elif url_path.startswith(settings.STATIC_URL):
                path = url_path.replace(settings.STATIC_URL, '')
                data['file_obj'] = open(find(path), 'rb')
                return data

        return weasyprint.default_url_fetcher(url, timeout, ssl_context)

    # Render HTML content
    html_content = render_to_string(template_name, context)

    # Determine base URL for assets (CSS, images, etc.)
    base_url = settings.WEASYPRINT_BASEURL if hasattr(settings, 'WEASYPRINT_BASEURL') else None
    if request:
        base_url = base_url or request.build_absolute_uri('/')

    # Generate PDF
    pdf_file = weasyprint.HTML(string=html_content, base_url=base_url, url_fetcher=django_url_fetcher).write_pdf()

    # Prepare HTTP response
    response = HttpResponse(pdf_file, content_type="application/pdf")
    disposition = "attachment" if attachment else "inline"
    response["Content-Disposition"] = f"{disposition}; filename={output_filename}"
    return response
