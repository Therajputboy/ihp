# Admin Route Report API Documentation

## Overview
This API provides comprehensive route management and execution reporting capabilities for admin users. It includes:
- **Single unified endpoint** that returns both dashboard summary statistics AND detailed route report data
- **Dashboard metrics**: Total Routes, Total Trips, Total Distance
- **Detailed report grid** with route utilization metrics (trip tracking, route status, distance coverage)
- **Export functionality**: Excel and PDF file generation with professional formatting

## Base URL
```
/v2/app/admin/reports
```

## Authentication
All endpoints require JWT authentication. Include the JWT token in the cookie or Authorization header.

---

## Endpoints

### 1. Get Route Report (Combined with Summary Stats)
**Endpoint:** `GET /route-report`

**Description:** Retrieves both summary statistics AND detailed route report data with optional filtering. This is a unified endpoint that provides dashboard cards and full report grid data in a single call.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from_date` | string | No | Start date in format `YYYY-MM-DD` |
| `to_date` | string | No | End date in format `YYYY-MM-DD` |
| `route_id` | string | No | Specific route ID to filter results |

**Example Request:**
```bash
curl -X GET "http://localhost:8080/v2/app/admin/reports/route-report?from_date=2024-01-01&to_date=2024-12-31&route_id=route123" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Response (200 OK):**
```json
{
  "message": "Route report fetched successfully.",
  "summary": {
    "total_routes": 32,
    "total_trips": 320,
    "total_distance_km": 67350.00
  },
  "report_data": [
    {
      "route_name": "Peenya 1st",
      "total_distance_km": 210.50,
      "total_trips": 24,
      "completed_trips": 20,
      "in_progress_trips": 4,
      "status": "Active",
      "action": "view",
      "route_id": "route123",
      "state": "Karnataka",
      "city": "Bangalore"
    }
  ],
  "total_records": 32,
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "route_id_filter": "route123"
}
```

**Report Data Columns:**
| Column | Description | Example |
|--------|-------------|---------|
| `route_name` | Name of the route | Peenya 1st |
| `total_distance_km` | Planned/total route distance | 210.50 |
| `total_trips` | Total trips assigned to route | 24 |
| `completed_trips` | Successfully completed trips | 20 |
| `in_progress_trips` | Trips currently in progress | 4 |
| `status` | Route operational status | Active |
| `action` | Action type (view for detailed info) | view |
| `state` | Route state/province | Karnataka |
| `city` | Route city | Bangalore |

**Summary Fields:**
| Field | Description | Example |
|-------|-------------|---------|
| `total_routes` | Number of unique routes in date range | 32 |
| `total_trips` | Total trips across all routes | 320 |
| `total_distance_km` | Cumulative distance of all routes | 67350.00 |

---

### 2. Export Report to Excel
**Endpoint:** `POST /route-report/export/excel`

**Description:** Exports filtered route report data as Excel file (.xlsx).

**Request Body:**
```json
{
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "route_id": "route123",
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
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8080/v2/app/admin/reports/route-report/export/excel" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "report_data": [...]
  }' \
  -o route_report.xlsx
```

**Response:** Excel file download
- Filename: `route_report_YYYY-MM-DD_to_YYYY-MM-DD.xlsx`
- Includes:
  - Report title and date range
  - Summary statistics (Total Routes, Total Trips, Total Distance)
  - Detailed table with all filtered records
  - Professional formatting with colors and borders

---

### 3. Export Report to PDF
**Endpoint:** `POST /route-report/export/pdf`

**Description:** Exports filtered route report data as PDF file with optional company logo.

**Request Body:**
```json
{
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "route_id": "route123",
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
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8080/v2/app/admin/reports/route-report/export/pdf" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "company_logo": "https://example.com/logo.png",
    "report_data": [...]
  }' \
  -o route_report.pdf
```

**Response:** PDF file download
- Filename: `route_report_YYYY-MM-DD_to_YYYY-MM-DD.pdf`
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
async function loadRouteReport(fromDate, toDate, routeId = null) {
  const params = new URLSearchParams();
  params.append('from_date', fromDate);
  params.append('to_date', toDate);
  if (routeId) params.append('route_id', routeId);

  const response = await fetch(`/v2/app/admin/reports/route-report?${params}`, {
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
  const response = await fetch('/v2/app/admin/reports/route-report/export/excel', {
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
  link.download = `route_report_${fromDate}_to_${toDate}.xlsx`;
  link.click();
}

// Export to PDF using report data from the unified endpoint
async function exportToPDF(reportData, fromDate, toDate, companyLogo = null) {
  const response = await fetch('/v2/app/admin/reports/route-report/export/pdf', {
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
  link.download = `route_report_${fromDate}_to_${toDate}.pdf`;
  link.click();
}

// Example usage in React
function RouteReportDashboard() {
  const [summary, setSummary] = useState(null);
  const [reportData, setReportData] = useState([]);
  const [fromDate, setFromDate] = useState('2024-01-01');
  const [toDate, setToDate] = useState('2024-12-31');
  const [routeFilter, setRouteFilter] = useState('');

  const handleFilterApply = async () => {
    const data = await loadRouteReport(fromDate, toDate, routeFilter || null);
    setSummary(data.summary);
    setReportData(data.report_data);
  };

  return (
    <div>
      {/* Filter Section */}
      <div className="filter-section">
        <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} />
        <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} />
        <select value={routeFilter} onChange={(e) => setRouteFilter(e.target.value)}>
          <option value="">All Routes</option>
          <option value="route1">Peenya 1st</option>
          <option value="route2">Whitefield Express</option>
        </select>
        <button onClick={handleFilterApply}>Filter</button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="summary-cards">
          <Card title="Total Routes" value={summary.total_routes} icon="🗺️" />
          <Card title="Total Trips" value={summary.total_trips} icon="🚗" />
          <Card title="Total Distance" value={`${summary.total_distance_km} KM`} icon="📍" />
        </div>
      )}

      {/* Report Table */}
      <div className="report-section">
        <button onClick={() => exportToExcel(reportData, fromDate, toDate)}>Export Excel</button>
        <button onClick={() => exportToPDF(reportData, fromDate, toDate)}>Export PDF</button>
        <RouteReportTable data={reportData} />
      </div>
    </div>
  );
}
```

---

## Report Fields Explanation

### Summary Statistics (Included in GET /route-report)
- **Total Routes**: Count of unique routes within the selected date range
- **Total Trips**: Total trips across all routes in the date range
- **Total Distance (KM)**: Cumulative distance of all routes

### Report Grid Columns
- **Route Name**: Descriptive name of the route
- **Total Distance (KM)**: Planned/total distance for the route
- **Total Trips**: Number of trips assigned to this route
- **Completed Trips**: Successfully completed trips on this route
- **In Progress Trips**: Trips currently being executed
- **Status**: Current route status (Active, Inactive, Maintenance, etc.)

---

## Trip Status Breakdown

| Status | Count Field | Description |
|--------|-------------|-------------|
| Completed | `completed_trips` | Successfully finished route executions |
| In Progress | `in_progress_trips` | Active route executions currently running |
| Not Started | Implied | Trips assigned but not yet started |

**Calculation:** `total_trips = completed_trips + in_progress_trips + not_started_trips`

---

## Error Responses

**403 Forbidden:** Non-admin user attempts to access report
```json
{
  "message": "Only admin can access route reports."
}
```

**400 Bad Request:** Invalid date format or missing required parameters
```json
{
  "message": "Oops! Something went wrong. Please try again."
}
```

---

## Notes

- All timestamps are in **Asia/Kolkata** timezone
- Date filters are inclusive (from_date is 00:00, to_date is 23:59:59)
- Report data includes routes created within the date range
- Excel export includes professional formatting with blue headers
- PDF export can include company logo for branding
- Distance values are rounded to 2 decimal places
- Route status values: Active, Inactive, Completed, In Progress, Maintenance
- Trip counts are aggregated from driver routes with status filtering

---

## Dependencies

Required Python packages (already added to requirements.txt):
- `openpyxl==3.1.2` - Excel file generation
- `reportlab==4.0.4` - PDF file generation

---

## Integration Notes

1. **Unified Endpoint**: The route report endpoint returns both summary and detail data in one response, reducing API calls and ensuring data consistency.

2. **Trip Tracking**: Monitor route utilization through trip counts:
   - Completed trips show route execution success
   - In-progress trips indicate current activity
   - Can identify routes with low utilization

3. **Distance Metrics**: Track route distances to:
   - Monitor route planning accuracy
   - Identify high-utilization routes
   - Plan resource allocation

4. **Status Management**: Route status helps identify:
   - Active routes in use
   - Inactive routes awaiting activation
   - Routes under maintenance

5. **Performance**: The merged endpoint optimizes database queries by computing statistics while gathering report data.

6. **Export Functionality**: Both Excel and PDF exports include summary statistics for comprehensive stakeholder reporting.
