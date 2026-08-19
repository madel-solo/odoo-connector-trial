from odoo import SUPERUSER_ID, api


LEGACY_MODELS = (
    'orchida.trial.submission',
    'orchida.trial.contact.wizard',
)
LEGACY_MENU_NAMES = (
    'Orchida E-Invoicing (Trial)',
    'Submission Log',
    'Customers',
    'Companies',
    'Learn More / Contact',
)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    menus = env['ir.ui.menu'].search([('parent_id', '=', False)]).filtered(
        lambda menu: menu.name in LEGACY_MENU_NAMES
    )
    action_ids = [
        action.id
        for action in menus.mapped('action')
        if action._name == 'ir.actions.act_window'
    ]
    menus.unlink()
    if action_ids:
        env['ir.actions.act_window'].browse(action_ids).unlink()

    models = env['ir.model'].search([('model', 'in', LEGACY_MODELS)])
    env['ir.ui.view'].search([
        '|',
        ('model', 'in', LEGACY_MODELS),
        ('arch_db', 'ilike', 'orchida_trial_'),
    ]).unlink()
    if models:
        env['ir.model.fields'].with_context(_force_unlink=True).search([
            '|',
            ('name', 'like', 'orchida_trial_%'),
            ('model_id', 'in', models.ids),
        ]).unlink()
        env['ir.model.access'].search([('model_id', 'in', models.ids)]).unlink()
        models.with_context(_force_unlink=True).unlink()
