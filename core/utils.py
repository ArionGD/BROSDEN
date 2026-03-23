from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os

def render_to_pdf(template_src, context_dict={}):
    """Renders a Django template to a PDF byte string."""
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
    # This function helps pisa find static files like images
    def link_callback(uri, rel):
        """
        Convert HTML images to absolute paths for pisa.
        """
        # Resolve static files
        if uri.startswith(settings.STATIC_URL):
            path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
            # If not in static_root, try static_dirs
            if not os.path.isfile(path):
                for static_dir in settings.STATICFILES_DIRS:
                    path = os.path.join(static_dir, uri.replace(settings.STATIC_URL, ""))
                    if os.path.isfile(path):
                        break
        # Resolve media files
        elif uri.startswith(settings.MEDIA_URL):
            path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
        else:
            return uri

        # Make sure that file exists
        if not os.path.isfile(path):
            return uri
            
        return path

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
    if not pdf.err:
        return result.getvalue()
    return None
