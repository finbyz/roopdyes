import frappe
from collections import defaultdict

def execute(filters=None):
    columns = get_columns()
    data, chart = get_data(filters)
    return columns, data, None, chart


# ---------------------------------------------------
# Columns
# ---------------------------------------------------
def get_columns():
    return [
        {"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 120},
        {"label": "Manufacturing", "fieldname": "manufacturing", "fieldtype": "Currency", "width": 150},
        {"label": "Trading", "fieldname": "trading", "fieldtype": "Currency", "width": 150},
        {"label": "Total", "fieldname": "total", "fieldtype": "Currency", "width": 150},
        {"label": "Manufacturing %", "fieldname": "m_percent", "fieldtype": "Percent", "width": 130},
        {"label": "Trading %", "fieldname": "t_percent", "fieldtype": "Percent", "width": 130},
    ]


# ---------------------------------------------------
# Main Logic
# ---------------------------------------------------
def get_data(filters):

    # ✅ Use Submitted invoices only
    conditions = ["si.docstatus = 1"]

    if filters.get("company"):
        conditions.append("si.company = %(company)s")

    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")

    where_clause = " AND ".join(conditions)

    result = frappe.db.sql(f"""
        SELECT 
            YEAR(si.posting_date) as year_no,
            MONTH(si.posting_date) as month_no,
            DATE_FORMAT(si.posting_date, '%%b %%Y') as month_label,
            sii.sales_type,
            SUM(sii.base_net_amount) as amount
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE {where_clause}
        GROUP BY YEAR(si.posting_date), MONTH(si.posting_date), sii.sales_type
        ORDER BY year_no ASC, month_no ASC
    """, filters, as_dict=1)


    months = []
    month_map = defaultdict(lambda: {"manufacturing": 0, "trading": 0})

    for row in result:
        if row.month_label not in months:
            months.append(row.month_label)

        if row.sales_type == "Manufacturing":
            month_map[row.month_label]["manufacturing"] += row.amount or 0
        elif row.sales_type == "Trading":
            month_map[row.month_label]["trading"] += row.amount or 0


    # -------------------------------
    # Build Table Data (DESC)
    # -------------------------------
    data = []
    manufacturing_vals = []
    trading_vals = []

    for month in months:
        m = month_map[month]["manufacturing"]
        t = month_map[month]["trading"]
        total = m + t

        data.append({
            "month": month,
            "manufacturing": m,
            "trading": t,
            "total": total,
            "m_percent": round((m / total * 100) if total else 0, 2),
            "t_percent": round((t / total * 100) if total else 0, 2),
        })

        # ✅ Use RAW values (no lakh conversion)
        manufacturing_vals.append(round(m, 2))
        trading_vals.append(round(t, 2))


    # -------------------------------
    # Chart (RAW values)
    # -------------------------------
    chart = {
        "data": {
            "labels": months,
            "datasets": [
                {
                    "name": "Manufacturing",
                    "values": manufacturing_vals
                },
                {
                    "name": "Trading",
                    "values": trading_vals
                }
            ]
        },
        "type": "line",
        "colors": ["#ff5858", "#5e64ff"],
        "axisOptions": {
            "xAxisMode": "tick",
            "xIsSeries": 1
        },
        "lineOptions": {
            "regionFill": 0
        },
        "height": 300
    }

    return data, chart
