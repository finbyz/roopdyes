# Copyright (c) 2026, FinByz Tech Pvt Ltd and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    return columns, data, None, chart


def get_columns():
    return [
        {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 120},
        {"label": "Domestic", "fieldname": "domestic", "fieldtype": "Currency", "width": 150},
        {"label": "Export", "fieldname": "export", "fieldtype": "Currency", "width": 150},
        {"label": "Grand Total", "fieldname": "total", "fieldtype": "Currency", "width": 150},
        {"label": "Domestic %", "fieldname": "domestic_percent", "fieldtype": "Percent", "width": 120},
        {"label": "Export %", "fieldname": "export_percent", "fieldtype": "Percent", "width": 120},
    ]


def get_data(filters):
    company = filters.get("company")
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    company_currency = frappe.db.get_value("Company", company, "default_currency")

    invoices = frappe.db.sql("""
        SELECT 
            MONTHNAME(posting_date) as month,
            MONTH(posting_date) as month_no,
            SUM(CASE WHEN currency = %(currency)s THEN base_net_total ELSE 0 END) as domestic,
            SUM(CASE WHEN currency != %(currency)s THEN base_net_total ELSE 0 END) as export
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        AND company = %(company)s
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY month_no, month
        ORDER BY month_no
    """, {
        "company": company,
        "from_date": from_date,
        "to_date": to_date,
        "currency": company_currency
    }, as_dict=1)

    data = []

    for row in invoices:
        domestic = row.domestic or 0
        export = row.export or 0
        total = domestic + export

        data.append({
            "month": row.month,
            "domestic": domestic,
            "export": export,
            "total": total,
            "domestic_percent": (domestic / total * 100) if total else 0,
            "export_percent": (export / total * 100) if total else 0,
        })

    return data


def get_chart_data(data):
    labels = []
    domestic = []
    export = []

    for row in data:
        if row.get("month") != "Grand Total":
            labels.append(row.get("month"))
            domestic.append(row.get("domestic"))
            export.append(row.get("export"))

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": "Domestic", "values": domestic},
                {"name": "Export", "values": export},
            ]
        },
        "type": "line"
    }
