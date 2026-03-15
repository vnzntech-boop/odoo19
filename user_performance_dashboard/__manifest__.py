{
    'name': 'User Performance Dashboard',
    'version': '19.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'A personalized performance dashboard for logged-in users.',
    'description': """
        This module provides a custom dashboard for users to track their metrics.
        Includes a profile section with avatar, name, and job title.
    """,
    'depends': ['base', 'web'],
    'data': [
        'views/dashboard_views.xml',
    ],
    'author': 'Vnzn Tech',
    'license': 'LGPL-3',
    'company': 'Venzn',
    'maintainer': 'Venzn',
    'support': 'vnzntech@gmail.com',

    'currency':'USD',
    'price': 1.0,
    
    'assets': {
        'web.assets_backend': [
            'user_performance_dashboard/static/src/css/dashboard.css',
            'user_performance_dashboard/static/src/js/dashboard.js',
            'user_performance_dashboard/static/src/xml/dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
