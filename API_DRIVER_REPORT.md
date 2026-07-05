# Admin Driver Report API Documentation

## Overview
This API provides comprehensive driver performance reporting capabilities for admin users. It includes:
- **Single unified endpoint** that returns both dashboard summary statistics AND detailed report data
- **Dashboard metrics**: Total Drivers, Total Routes Completed, Total Diversions  
- **Detailed report grid** with driver performance metrics (route times, checkpoints, completion %, diversion status)
- **Export functionality**: Excel and PDF file generation with professional formatting

## Base URL
```
/v2/app/admin/reports
```

## Authentication
All endpoints require JWT authentication. Include the JWT token in the cookie or Authorization header.

---

## Endpoints

### 1. Get Driver Report (Combined with Summary Stats)
**Endpoint:** `GET /driver-report`

**Description:** Retrieves both summary statistics AND detailed driver report data with optional filtering. This is a unified endpoint that provides dashboard cards and full report grid data in a single call.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from_date` | string | No | Start date in format `YYYY-MM-DD` |
| `to_date` | string | No | End date in format `YYYY-MM-DD` |
| `driver_id` | string | No | Specific driver ID to filter results |

**Example Request:**
```bash
curl -X GET "http://localhost:8080/v2/app/admin/reports/driver-report?from_date=2024-01-01&to_date=2024-12-31&driver_id=driver123" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Response (200 OK):**
```json
{
  "message": "Driver report fetched successfully.",
  "summary": {
    "total_drivers": 24,
    "total_routes_completed": 156,
    "total_diversions": 28
  },
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
      "status": "Completed",
      "action": "view",
      "route_id": "route123",
      "driver_ids": ["driver123"]
    }
  ],
  "total_records": 1,
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "driver_id_filter": "driver123"
}
```

**Report Data Columns:**
| Column | Description |
|--------|-------------|
| `driver_name` | Name of the driver |
| `assigned_route` | Route name assigned to the driver |
| `assigned_truck` | Truck ID/Number assigned |
| `route_start_time` | Actual route start date and time |
| `route_end_time` | Actual route completion date and time |
| `total_time_taken` | Total duration to complete the route |
| `checkpoints_covered` | Covered checkpoints / Total checkpoints (e.g., 12/15) |
| `completion_percentage` | Route completion percentage (Covered/Total * 100) |
| `diversion` | Yes/No indicator for route diversions |
| `diversion_count` | Number of route deviations detected |
| `status` | Route execution status (Completed/In Progress) |
| `action` | Action type (view for detailed route information) |

---

### 2. Get Summary Statistics
**Endpoint:** `GET /driver-report/summary-stats`

**Description:** Retrieves dashboard summary cards with aggregated statistics.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from_date` | string | No | Start date in format `YYYY-MM-DD` |
| `to_date` | string | No | End date in format `YYYY-MM-DD` |

**Example Request:**
```bash
curl -X GET "http://localhost:8080/v2/app/admin/reports/driver-report/summary-stats?from_date=2024-01-01&to_date=2024-12-31" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Response (200 OK):**
```json
{
  "message": "Summary statistics fetched successfully.",
  "summary": {
    "total_drivers": 24,
    "total_routes_completed": 156,
    "total_diversions": 28
  },
  "from_date": "2024-01-01",
  "to_date": "2024-12-31"
}
```

**Summary Fields:**
| Field | Description | Example |
|-------|-------------|---------|
| `total_drivers` | Number of unique active drivers | 24 |
| `total_routes_completed` | Total completed routes in date range | 156 |
| `total_diversions` | Total route deviations detected | 28 |

---

### 2. Export Report to Excel
**Endpoint:** `POST /driver-report/export/excel`

**Description:** Exports filtered driver report data as Excel file (.xlsx).

**Request Body:**
```json
{
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "driver_id": "driver123",
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
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8080/v2/app/admin/reports/driver-report/export/excel" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "report_data": [...]
  }' \
  -o driver_report.xlsx
```

**Response:** Excel file download
- Filename: `driver_report_YYYY-MM-DD_to_YYYY-MM-DD.xlsx`
- Includes:
  - Report title and date range
  - Summary statistics (Total Drivers, Total Routes, Total Diversions)
  - Detailed table with all filtered records
  - Professional formatting with colors and borders

---

### 3. Export Report to PDF
**Endpoint:** `POST /driver-report/export/pdf`

**Description:** Exports filtered driver report data as PDF file with optional company logo.

**Request Body:**
```json
{
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "driver_id": "driver123",
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
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8080/v2/app/admin/reports/driver-report/export/pdf" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "company_logo": "https://example.com/logo.png",
    "report_data": [...]
  }' \
  -o driver_report.pdf
```

**Response:** PDF file download
- Filename: `driver_report_YYYY-MM-DD_to_YYYY-MM-DD.pdf`
- Includes:
  - Company logo (if provided)
  - Report title and date range
  - Summary statistics
  - Professional table with all filtered records
  - Page breaks for long reports

---

## Usage Flow

### Frontend Integration Example

```javascript
// Single unified endpoint that returns BOTH summary stats and report data
async function loadDriverReport(fromDate, toDate, driverId = null) {
  const params = new URLSearchParams();
  params.append('from_date', fromDate);
  params.append('to_date', toDate);
  if (driverId) params.append('driver_id', driverId);

  const response = await fetch(`/v2/app/admin/reports/driver-report?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  
  // Extract summary and report data from single response
  const { summary, report_data } = data;
  
  // Display dashboard summary cards
  displaySummaryStats(summary);
  
  // Display detailed report table
  displayReportTable(report_data);
  
  return data;
}

// Export to Excel using report data from the unified endpoint
async function exportToExcel(reportData, fromDate, toDate) {
  const response = await fetch('/v2/app/admin/reports/driver-report/export/excel', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      from_date: fromDate,
      to_date: toDate,
      report_data: reportData
    })
  });

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `driver_report_${fromDate}_to_${toDate}.xlsx`;
  link.click();
}

// Export to PDF using report data from the unified endpoint
async function exportToPDF(reportData, fromDate, toDate, companyLogo = null) {
  const response = await fetch('/v2/app/admin/reports/driver-report/export/pdf', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      from_date: fromDate,
      to_date: toDate,
      company_logo: companyLogo,
      report_data: reportData
    })
  });

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `driver_report_${fromDate}_to_${toDate}.pdf`;
  link.click();
}

// Example usage in React
function DriverReportDashboard() {
  const [summary, setSummary] = useState(null);
  const [reportData, setReportData] = useState([]);
  const [fromDate, setFromDate] = useState('2024-01-01');
  const [toDate, setToDate] = useState('2024-12-31');

  const handleFilterApply = async () => {
    const data = await loadDriverReport(fromDate, toDate);
    setSummary(data.summary);
    setReportData(data.report_data);
  };

  return (
    <div>
      {/* Filter Section */}
      <div className="filter-section">
        <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} />
        <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} />
        <button onClick={handleFilterApply}>Filter</button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="summary-cards">
          <Card title="Total Drivers" value={summary.total_drivers} icon="👥" />
          <Card title="Total Routes Completed" value={summary.total_routes_completed} icon="🚗" />
          <Card title="Total Diversions" value={summary.total_diversions} icon="⚠️" />
        </div>
      )}

      {/* Report Table */}
      <div className="report-section">
        <button onClick={() => exportToExcel(reportData, fromDate, toDate)}>Export Excel</button>
        <button onClick={() => exportToPDF(reportData, fromDate, toDate)}>Export PDF</button>
        <ReportTable data={reportData} />
      </div>
    </div>
  );
}
```

---

## Error Responses

**403 Forbidden:** Non-admin user attempts to access report
```json
{
  "message": "Only admin can access driver reports."
}
```

**400 Bad Request:** Invalid date format or missing required parameters
```json
{
  "message": "Oops! Something went wrong. Please try again."
}
```

---

## Report Fields Explanation

### Summary Statistics (Included in GET /driver-report)
- **Total Drivers**: Count of unique drivers with completed routes in the selected date range
- **Total Routes Completed**: Count of all completed and approved routes in the date range
- **Total Diversions**: Aggregate count of all route deviations detected across all routes

### Report Grid Columns
- **Driver Name**: Name of the driver(s) assigned to the route
- **Assigned Route**: Name/ID of the route
- **Assigned Truck**: Truck ID/Number used for the route
- **Route Start Time**: When the driver started the route (formatted: DD-Mon-YYYY HH:MM AM/PM)
- **Route End Time**: When the driver completed the route (formatted: DD-Mon-YYYY HH:MM AM/PM)
- **Total Time Taken**: Duration = Route End Time - Route Start Time (formatted: X Hours Y Minutes)
- **Checkpoints Covered**: Ratio format (covered/total), e.g., "12/15"
- **Completion %**: Percentage = (Covered Checkpoints / Total Checkpoints) × 100
- **Diversion**: "Yes" if any route deviations were detected, "No" otherwise
- **Status**: Route execution status - "Completed" for finalized routes

## Notes

- All timestamps are in **Asia/Kolkata** timezone
- Date filters are inclusive (from_date is 00:00, to_date is 23:59:59)
- Report data only includes **completed and approved routes**
- Excel export includes professional formatting with headers, summary statistics, and borders
- PDF export can include company logo for branding
- Total time calculation: Route End Time - Route Start Time
- Completion percentage helps identify route compliance and checkpoint coverage
- Diversion indicator helps identify route compliance issues

---

## Dependencies

Required Python packages (already added to requirements.txt):
- `openpyxl==3.1.2` - Excel file generation
- `reportlab==4.0.4` - PDF file generation

Install with:
```bash
pip install -r requirements.txt
```
