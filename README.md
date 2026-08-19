# Orchida UAE E-Invoicing Trial

Public UI-only trial modules for the Orchida UAE E-Invoicing Connector.

## Branches

| Branch | Odoo version |
| --- | --- |
| `16.0` | Odoo 16 |
| `17.0` | Odoo 17 |
| `18.0` | Odoo 18 |
| `19.0` | Odoo 19 |

Each version branch contains the complete `orchida_uae_e_invoicing`
module in its own folder at repository root.

## Trial Scope

The trial module mirrors the connector's screens, fields, menus, and sample
data so you can evaluate the user experience in Odoo. It does not contain the
production integration backend.

The trial does not include API clients, credentials, payload builders, tax
validation, cron jobs, invoice submission, or external API calls. Trial action
buttons show a message directing users to the full connector.

## Installation

1. Select the branch for your Odoo version.
2. Copy the `orchida_uae_e_invoicing/` folder into an Odoo addons path.
3. Update the Apps list and install **Orchida UAE E-Invoicing Connector for Odoo**.

The module depends on Odoo `base`, `account`, and `product`.

## License

This repository is released under the Odoo Proprietary License v1.0 (`OPL-1`).
See [`LICENSE`](LICENSE). The repository is public for evaluation and source
reference; publication does not grant permission to redistribute, sublicense,
or sell the module.

## Contact

For production integration, licensing, or support, visit the [Orchida Odoo
e-invoicing integration page](https://orchidatax.com/e-invoicing-integration-solutions/erp-integrations/odoo).
