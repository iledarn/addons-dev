# -*- coding: utf-8 -*-
{
    "name": """Limited number of records""",
    "summary": """e.g. limit number of users by three""",
    "category": "Extra tools",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Pavel Romanchenko",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    "price": 30.00,
    "currency": "EUR",

    "depends": [
        'base_action_rule',
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/base_limit.xml',
        'data/data.xml',
        'security/records_number_security.xml',
        'security/ir.model.access.csv',
    ],
    "qweb": [],
    "demo": [],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
}
