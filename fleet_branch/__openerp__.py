# -*- coding: utf-8 -*-
{
    "name": "Fleet branch",
    "summary": """Manage branches of fleet""",
    "category": "Managing vehicles and contracts",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    # 'price': 40000.00,
    # 'currency': 'EUR',

    "depends": [
        "hr",
        "fleet",
        "l10n_sa",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/fleet_branch.xml",
        "data/ir_sequence.xml",
        "security/fleet_branch.xml",
        'security/ir.model.access.csv',
    ],
    "qweb": [
    ],
    "demo": [],
    'installable': True,
    "auto_install": False,
}
