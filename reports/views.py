from django.shortcuts import render
import json

def charts(request):
    chart_data = {
        "labels": ["Jan", "Feb", "Mar"],
        "values": [10, 20, 30]
    }
    return render(request, "chart.html", {"chart_data": json.dumps(chart_data)})
