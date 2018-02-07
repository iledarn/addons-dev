# -*- coding: utf-8 -*-
{
    "name": """Multi Website Blog""",
    "summary": """Specify eligible websites for your blogs""",
    "category": "eCommerce",
    # "live_test_url": "",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/iledarn",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "website_blog",
        "website_multi_company",
        "ir_rule_website",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/website_blog_views.xml',
        'security/blog_security.xml',
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}