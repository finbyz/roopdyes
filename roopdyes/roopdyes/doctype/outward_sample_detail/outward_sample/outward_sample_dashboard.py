from frappe import _

def get_data():
	return {
		'fieldname': 'prevdoc_docname',
		'non_standard_fieldnames': {
			'Inward Sample': 'outward_reference_1',
			'Outward Tracking': 'sample_ref'
		},
		'transactions': [
			{
				'items': ['Inward Sample', 'Outward Tracking']
			},
		]
	}