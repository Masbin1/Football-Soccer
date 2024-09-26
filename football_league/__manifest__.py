{
    'name': 'Soccer League',
    'version': '1.0',
    'category': 'Sports',
    'summary': 'Manage soccer league standings',
    'description': """
        This module allows you to:
        - Input club data
        - Input match scores
        - View league standings
    """,
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/club_views.xml',
        'views/match_views.xml',
        'views/standing_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}