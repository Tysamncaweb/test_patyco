{
        'name': "Coordinadora Integration",
        'version': '1.0',
        'depends': ['base'],
        'author': "Ing. José A. Colmenares B."
                  "Ing. Yorman J. Pineda F.",
        'category': 'Integration',
        'description': """
        Este modulo esta diseñado para realizar el consumo de la API de la empresa Coordinadora Mercantil S.A., la cual permitira realizar acciones como realizar generar guias, etiquetas, imprimir guias, rastreo de guias, entre otras funciones.
        """,
        # data files always loaded at installation
        'data': [
            'security/ir.model.access.csv',
            'data/settings_data.xml',
            'data/departments_data.xml',
            'data/code_danes_data.xml',
            'views/generate_guide_view.xml',
            'views/settings_view.xml',
	        'views/generate_guide_inter_view.xml',
            'views/liquidar_guia_view.xml',
            'views/settings_department_view.xml',
            'views/settings_codes_danes_view.xml',
            'views/generate_label_view.xml',
            'views/simple_tracking_view.xml',
            'views/pickup_tracking_view.xml',
            'wizard/print_documents_view.xml',
            'wizard/update_codes_danes_view.xml',
            'wizard/print_guide_view.xml',
            #'views/prueba.xml',

        ],
        # data files containing optionally loaded demonstration data
        'update_xml':[
            #'data/departamentos.sql',
            #'data/codigos_danes.sql',
        ],
        'installable': True,
        'auto_install': True,
        'application': True,
    }
