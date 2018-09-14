from frappe import _

def get_data():
	return {
		'fieldname': 'against',
		'non_standard_fieldnames': {
			'Outward Sample': 'inward_sample'
		},
		'transactions': [
			{	
				'label': _('Outward Items'),
				'items': ['Outward Sample']
			},	
		]
	}