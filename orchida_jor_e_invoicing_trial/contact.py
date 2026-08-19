from odoo import _
from odoo.exceptions import RedirectWarning

CONTACT_URL = "https://orchidatax.com/about-us/orchida-profile-enterprise-e-invoicing/#ox-contact"
CONTACT_MESSAGE = (
    "This capability is available in the full Orchida UAE E-Invoicing Connector. "
    "Contact Orchida to activate it."
)
CONTACT_BUTTON = "Contact Orchida"


def raise_contact_message():
    """Raise a redirect dialog that opens the Orchida contact page."""
    raise RedirectWarning(
        _(CONTACT_MESSAGE),
        {
            'type': 'ir.actions.act_url',
            'url': CONTACT_URL,
            'target': 'new',
        },
        _(CONTACT_BUTTON),
    )
