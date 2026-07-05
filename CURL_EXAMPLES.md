# Admin Report APIs - CURL Examples

This document contains curl commands for testing all three admin report APIs: Driver Report, Truck Report, and Route Report.

## Base Configuration

```bash
# Set these variables for easier usage
export BASE_URL="http://localhost:8080/v2/app/admin/reports"
export TOKEN="your_jwt_token_here"
export FROM_DATE="2024-01-01"
export TO_DATE="2024-12-31"
```

---

## 1. DRIVER REPORT API

### 1.1 Get Driver Report (All Drivers)
```bash
curl -X GET \
  "${BASE_URL}/driver-report?from_date=${FROM_DATE}&to_date=${TO_DATE}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"
```

### 1.2 Get Driver Report (Specific Driver)
```bash
curl -X GET \
  "${BASE_URL}/driver-report?from_date=${FROM_DATE}&to_date=${TO_DATE}&driver_id=driver123" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"
```

### 1.3 Get Driver Report (No Date Filter)
```bash
curl -X GET \
  "${BASE_URL}/driver-report" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"
```

### 1.4 Export Driver Report to Excel
```bash
curl -X POST \
  "${BASE_URL}/driver-report/export/excel" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "report_data": [
      {
        "driver_name": "Rahul Sharma",
        "assigned_route": "Peenya 1st",
        "assigned_truck": "TRK-101",
        "route_start_time": "01-May-2024 08:15 AM",
        "route_end_time": "01-May-2024 05:45 PM",
        "total_time_taken": "9 Hours 30 Minutes",
        "checkpoints_covered": "12/15",
        "completion_percentage": "80%",
        "diversion": "Yes",
        "diversion_count": 2,
        "status": "Completed"
      }
    ]
  }' \
  -o driver_report_2024-01-01_to_2024-12-31.xlsx
```

### 1.5 Export Driver Report to PDF
```bash
curl -X POST \
  "${BASE_URL}/driver-report/export/pdf" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "company_logo": "https://example.com/logo.png",
    "report_data": [
      {
        "driver_name": "Rahul Sharma",
        "assigned_route": "Peenya 1st",
        "assigned_truck": "TRK-101",
        "route_start_time": "01-May-2024 08:15 AM",
        "route_end_time": "01-May-2024 05:45 PM",
        "total_time_taken": "9 Hours 30 Minutes",
        "checkpoints_covered": "12/15",
        "completion_percentage": "80%",
        "diversion": "Yes",
        "diversion_count": 2,
        "status": "Completed"
      }
    ]
  }' \
  -o driver_report_2024-01-01_to_2024-12-31.pdf
```

### 1.6 Export Driver Report to PDF (Without Logo)
```bash
curl -X POST \
  "${BASE_URL}/driver-report/export/pdf" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "report_data": []
  }' \
  -o driver_report.pdf
```

---

## 2. TRUCK REPORT API

### 2.1 Get Truck Report (All Trucks)
```bash
curl -X GET \
  "${BASE_URL}/truck-report?from_date=${FROM_DATE}&to_date=${TO_DATE}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"
```

### 2.2 Get Truck Report (Specific Truck)
```bash
curl -X GET \
  "${BASE_URL}/truck-report?from_date=${FROM_DATE}&to_date=${TO_DATE}&truck_id=TRK-101" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"
```

### 2.3 Get Truck Report (No Date Filter)
```bash
curl -X GET \
  "${BASE_URL}/truck-report" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"
```

### 2.4 Export Truck Report to Excel
```bash
curl -X POST \
  "${BASE_URL}/truck-report/export/excel" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "report_data": [
      {
        "truck_number": "TRK-101",
        "date": "01/05/2024",
        "route_assigned": "Peenya 1st",
        "driver_1": "Rahul Sharma",
        "driver_2": "Suresh Yadav",
        "total_distance_km": 210.50,
        "actual_distance_km": 235.40,
        "extra_distance_km": 24.90,
        "damage_reported": "No",
        "status": "Active"
      }
    ]
  }' \
  -o truck_report_2024-01-01_to_2024-12-31.xlsx
```

### 2.5 Export Truck Report to PDF
```bash
curl -X POST \
  "${BASE_URL}/truck-report/export/pdf" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "company_logo": "https://example.com/logo.png",
    "report_data": [
      {
        "truck_number": "TRK-101",
        "date": "01/05/2024",
        "route_assigned": "Peenya 1st",
        "driver_1": "Rahul Sharma",
        "driver_2": "Suresh Yadav",
        "total_distance_km": 210.50,
        "actual_distance_km": 235.40,
        "extra_distance_km": 24.90,
        "damage_reported": "No",
        "status": "Active"
      }
    ]
  }' \
  -o truck_report_2024-01-01_to_2024-12-31.pdf
```

### 2.6 Export Truck Report to PDF (Without Logo)
```bash
curl -X POST \
  "${BASE_URL}/truck-report/export/pdf" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "report_data": []
  }' \
  -o truck_report.pdf
```

---

## 3. ROUTE REPORT API

### 3.1 Get Route Report (All Routes)
```bash
curl -X GET \
  "${BASE_URL}/route-report?from_date=${FROM_DATE}&to_date=${TO_DATE}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"
```

### 3.2 Get Route Report (Specific Route)
```bash
curl -X GET \
  "${BASE_URL}/route-report?from_date=${FROM_DATE}&to_date=${TO_DATE}&route_id=route123" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"
```

### 3.3 Get Route Report (No Date Filter)
```bash
curl -X GET \
  "${BASE_URL}/route-report" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"
```

### 3.4 Export Route Report to Excel
```bash
curl -X POST \
  "${BASE_URL}/route-report/export/excel" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "report_data": [
      {
        "route_name": "Peenya 1st",
        "total_distance_km": 210.50,
        "total_trips": 24,
        "completed_trips": 20,
        "in_progress_trips": 4,
        "status": "Active"
      }
    ]
  }' \
  -o route_report_2024-01-01_to_2024-12-31.xlsx
```

### 3.5 Export Route Report to PDF
```bash
curl -X POST \
  "${BASE_URL}/route-report/export/pdf" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "company_logo": "https://example.com/logo.png",
    "report_data": [
      {
        "route_name": "Peenya 1st",
        "total_distance_km": 210.50,
        "total_trips": 24,
        "completed_trips": 20,
        "in_progress_trips": 4,
        "status": "Active"
      }
    ]
  }' \
  -o route_report_2024-01-01_to_2024-12-31.pdf
```

### 3.6 Export Route Report to PDF (Without Logo)
```bash
curl -X POST \
  "${BASE_URL}/route-report/export/pdf" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "report_data": []
  }' \
  -o route_report.pdf
```

---

## Quick Test Script

Save this as `test_apis.sh` and run it for quick testing:

```bash
#!/bin/bash

# Configuration
BASE_URL="http://localhost:8080/v2/app/admin/reports"
TOKEN="your_jwt_token_here"
FROM_DATE="2024-01-01"
TO_DATE="2024-12-31"

echo "====== DRIVER REPORT TESTS ======"
echo "1. Get Driver Report (All Drivers)"
curl -X GET \
  "${BASE_URL}/driver-report?from_date=${FROM_DATE}&to_date=${TO_DATE}" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

echo -e "\n2. Get Driver Report (Specific Driver)"
curl -X GET \
  "${BASE_URL}/driver-report?from_date=${FROM_DATE}&to_date=${TO_DATE}&driver_id=driver123" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

echo -e "\n====== TRUCK REPORT TESTS ======"
echo "3. Get Truck Report (All Trucks)"
curl -X GET \
  "${BASE_URL}/truck-report?from_date=${FROM_DATE}&to_date=${TO_DATE}" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

echo -e "\n4. Get Truck Report (Specific Truck)"
curl -X GET \
  "${BASE_URL}/truck-report?from_date=${FROM_DATE}&to_date=${TO_DATE}&truck_id=TRK-101" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

echo -e "\n====== ROUTE REPORT TESTS ======"
echo "5. Get Route Report (All Routes)"
curl -X GET \
  "${BASE_URL}/route-report?from_date=${FROM_DATE}&to_date=${TO_DATE}" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

echo -e "\n6. Get Route Report (Specific Route)"
curl -X GET \
  "${BASE_URL}/route-report?from_date=${FROM_DATE}&to_date=${TO_DATE}&route_id=route123" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

echo -e "\n✓ All tests completed"
```

Run with:
```bash
chmod +x test_apis.sh
./test_apis.sh
```

---

## Common HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Report data returned successfully |
| 400 | Bad Request | Invalid date format or missing parameters |
| 403 | Forbidden | User is not an admin |
| 500 | Server Error | Internal server error |

---

## Troubleshooting

### Issue: "Invalid token" or 403 Forbidden
```bash
# Ensure token is valid and set correctly
echo $TOKEN

# Re-login to get a new token if expired
curl -X POST "http://localhost:8080/v2/app/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "userid": "admin123",
    "password": "password123"
  }' | jq '.token'
```

### Issue: Empty report data
Check that:
1. Date range includes data: `from_date` should be before `to_date`
2. Filter ID exists (driver_id, truck_id, or route_id)
3. Data has been created in the system

### Issue: Export file not created
Make sure curl can write to the current directory, or specify full path:
```bash
curl -X POST "${BASE_URL}/driver-report/export/excel" \
  ... \
  -o /full/path/to/driver_report.xlsx
```

---

## Pretty Print JSON Responses

Install `jq` for better JSON formatting:
```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq
```

Then pipe responses through jq:
```bash
curl -X GET "${BASE_URL}/driver-report?from_date=${FROM_DATE}&to_date=${TO_DATE}" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

---

## Save Response to File

```bash
# Save JSON response
curl -X GET "${BASE_URL}/driver-report?from_date=${FROM_DATE}&to_date=${TO_DATE}" \
  -H "Authorization: Bearer ${TOKEN}" \
  > driver_report_response.json

# View saved response
cat driver_report_response.json | jq '.'
```

---

## Postman Collection Import

You can also import these APIs into Postman. Create a file `admin-reports.postman_collection.json`:

```json
{
  "info": {
    "name": "Admin Report APIs",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Driver Report",
      "item": [
        {
          "name": "Get Driver Report",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{base_url}}/driver-report?from_date=2024-01-01&to_date=2024-12-31",
              "protocol": "http"
            },
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ]
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8080/v2/app/admin/reports"
    },
    {
      "key": "token",
      "value": "your_jwt_token_here"
    }
  ]
}
```

Import this into Postman via: `File > Import > Paste Raw Text`

---

## API Summary

| API | Base URL | Endpoints | Status |
|-----|----------|-----------|--------|
| Driver Report | `/v2/app/admin/reports` | 3 endpoints | ✅ Ready |
| Truck Report | `/v2/app/admin/reports` | 3 endpoints | ✅ Ready |
| Route Report | `/v2/app/admin/reports` | 3 endpoints | ✅ Ready |

**Total:** 9 endpoints across 3 report modules
