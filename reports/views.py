from django.shortcuts import render
import json
from django.http import JsonResponse  # Import JsonResponse


def charts(request):
    chart_data = {
        "labels": ["Jan", "Feb", "Mar"],
        "values": [10, 20, 30]
    }
    return render(request, "chart.html", {"chart_data": json.dumps(chart_data)})

# Sample Data (Replace this with database queries later)
dashboard_data = {
    "total_orders": 30,
    "avg_order_value": 534.21,
    "pending_orders": 8,
    "total_sales": "16.03K",
    "total_income": "7.26K",
    "sales_by_year": [12000, 15000, 10000],  # Data for line chart
    "order_status": [10, 26, 6, 20, 23]  # Data for doughnut chart
}

def donut(request):
    return render(request, 'donut.html')

def get_dashboard_data(request):
    return JsonResponse(dashboard_data)