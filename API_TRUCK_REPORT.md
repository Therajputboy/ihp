# Admin Truck Report API Documentation

## Overview
This API provides comprehensive truck fleet management reporting capabilities for admin users. It includes:
- **Single unified endpoint** that returns both dashboard summary statistics AND detailed truck report data
- **Dashboard metrics**: Total Trucks, Total Trips, Total Distance  
- **Detailed report grid** with truck utilization metrics (distance tracking, damage reports, operational status)
- **Export functionality**: Excel and PDF file generation with professional formatting

## Base URL
```
/v2/app/admin/reports
```

## Authentication
All endpoints require JWT authentication. Include the JWT token in the cookie or Authorization header.

---

## Endpoints

### 1. Get Truck Report (Combined with Summary Stats)
**Endpoint:** `GET /truck-report`

**Description:** Retrieves both summary statistics AND detailed truck report data with optional filtering. This is a unified endpoint that provides dashboard cards and full report grid data in a single call.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from_date` | string | No | Start date in format `YYYY-MM-DD` |
| `to_date` | string | No | End date in format `YYYY-MM-DD` |
| `truck_id` | string | No | Specific truck ID to filter results |

**Example Request:**
```bash
curl -X GET "http://localhost:8080/v2/app/admin/reports/truck-report?from_date=2024-01-01&to_date=2024-12-31&truck_id=TRK-101" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Response (200 OK):**
```json
{
  "message": "Truck report fetched successfully.",
  "summary": {
    "total_trucks": 18,
    "total_trips": 142,
    "total_distance_km": 28540.50
  },
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
      "status": "Active",
      "action": "view",
      "truckid": "TRK-101",
      "route_id": "route123"
    }
  ],
  "total_records": 142,
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "truck_id_filter": "TRK-101"
}
```

**Report Data Columns:**
| Column | Description | Example |
|--------|-------------|---------|
| `truck_number` | Truck registration number | TRK-101 |
| `date` | Route execution date | 01/05/2024 |
| `route_assigned` | Assigned route name | Peenya 1st |
| `driver_1` | Primary assigned driver | Rahul Sharma |
| `driver_2` | Secondary assigned driver (if any) | Suresh Yadav |
| `total_distance_km` | Approved/planned route distance | 210.50 |
| `actual_distance_km` | GPS tracked actual distance | 235.40 |
| `extra_distance_km` | Additional distance beyond planned | 24.90 |
| `damage_reported` | Truck damage indicator (Yes/No) | No |
| `status` | Truck operational status | Active |
| `action` | Action type (view for detailed info) | view |

**Summary Fields:**
| Field | Description | Example |
|-------|-------------|---------|
| `total_trucks` | Number of unique trucks in date range | 18 |
| `total_trips` | Total completed trips | 142 |
| `total_distance_km` | Cumulative distance travelled | 28540.50 |

---

### 2. Export Report to Excel
**Endpoint:** `POST /truck-report/export/excel`

**Description:** Exports filtered truck report data as Excel file (.xlsx).

**Request Body:**
```json
{
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "truck_id": "TRK-101",
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
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8080/v2/app/admin/reports/truck-report/export/excel" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "report_data": [...]
  }' \
  -o truck_report.xlsx
```

**Response:** Excel file download
- Filename: `truck_report_YYYY-MM-DD_to_YYYY-MM-DD.xlsx`
- Includes:
  - Report title and date range
  - Summary statistics (Total Trucks, Total Trips, Total Distance)
  - Detailed table with all filtered records
  - Professional formatting with colors and borders

---

### 3. Export Report to PDF
**Endpoint:** `POST /truck-report/export/pdf`

**Description:** Exports filtered truck report data as PDF file with optional company logo.

**Request Body:**
```json
{
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "truck_id": "TRK-101",
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
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8080/v2/app/admin/reports/truck-report/export/pdf" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "company_logo": "https://example.com/logo.png",
    "report_data": [...]
  }' \
  -o truck_report.pdf
```

**Response:** PDF file download
- Filename: `truck_report_YYYY-MM-DD_to_YYYY-MM-DD.pdf`
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
async function loadTruckReport(fromDate, toDate, truckId = null) {
  const params = new URLSearchParams();
  params.append('from_date', fromDate);
  params.append('to_date', toDate);
  if (truckId) params.append('truck_id', truckId);

  const response = await fetch(`/v2/app/admin/reports/truck-report?${params}`, {
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
  const response = await fetch('/v2/app/admin/reports/truck-report/export/excel', {
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
  link.download = `truck_report_${fromDate}_to_${toDate}.xlsx`;
  link.click();
}

// Export to PDF using report data from the unified endpoint
async function exportToPDF(reportData, fromDate, toDate, companyLogo = null) {
  const response = await fetch('/v2/app/admin/reports/truck-report/export/pdf', {
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
  link.download = `truck_report_${fromDate}_to_${toDate}.pdf`;
  link.click();
}

// Example usage in React
function TruckReportDashboard() {
  const [summary, setSummary] = useState(null);
  const [reportData, setReportData] = useState([]);
  const [fromDate, setFromDate] = useState('2024-01-01');
  const [toDate, setToDate] = useState('2024-12-31');
  const [truckFilter, setTruckFilter] = useState('');

  const handleFilterApply = async () => {
    const data = await loadTruckReport(fromDate, toDate, truckFilter || null);
    setSummary(data.summary);
    setReportData(data.report_data);
  };

  return (
    <div>
      {/* Filter Section */}
      <div className="filter-section">
        <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} />
        <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} />
        <select value={truckFilter} onChange={(e) => setTruckFilter(e.target.value)}>
          <option value="">All Trucks</option>
          <option value="TRK-101">TRK-101</option>
          <option value="TRK-102">TRK-102</option>
        </select>
        <button onClick={handleFilterApply}>Filter</button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="summary-cards">
          <Card title="Total Trucks" value={summary.total_trucks} icon="🚚" />
          <Card title="Total Trips" value={summary.total_trips} icon="🛣️" />
          <Card title="Total Distance" value={`${summary.total_distance_km} KM`} icon="📍" />
        </div>
      )}

      {/* Report Table */}
      <div className="report-section">
        <button onClick={() => exportToExcel(reportData, fromDate, toDate)}>Export Excel</button>
        <button onClick={() => exportToPDF(reportData, fromDate, toDate)}>Export PDF</button>
        <TruckReportTable data={reportData} />
      </div>
    </div>
  );
}
```

---

## Report Fields Explanation

### Summary Statistics (Included in GET /truck-report)
- **Total Trucks**: Count of unique trucks with completed routes in the selected date range
- **Total Trips**: Count of all completed trips in the date range
- **Total Distance (KM)**: Cumulative GPS tracked distance travelled by all trucks

### Report Grid Columns
- **Truck Number**: Truck registration/identification number
- **Date**: Route execution date (format: DD/MM/YYYY)
- **Route Assigned**: Name/ID of the assigned route
- **Driver 1**: Primary driver assigned to the truck
- **Driver 2**: Secondary driver (co-driver) if applicable
- **Total Distance (KM)**: Approved/planned route distance
- **Actual Distance (KM)**: GPS tracked actual distance travelled
- **Extra Distance (KM)**: Additional distance = Actual - Total (indicates deviation)
- **Damage Reported**: "Yes" if any vehicle damage was reported, "No" otherwise
- **Status**: Truck operational status (Active, Maintenance, Out of Service)

---

## Error Responses

**403 Forbidden:** Non-admin user attempts to access report
```json
{
  "message": "Only admin can access truck reports."
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
- Report data only includes **completed and approved routes**
- Excel export includes professional formatting with orange headers (brand color)
- PDF export can include company logo for branding
- Extra distance calculation: Actual Distance - Total Distance (positive value indicates deviation)
- Distance values are rounded to 2 decimal places
- Status values: Active, Maintenance, Out of Service
- Damage reporting helps identify vehicle maintenance needs

---

## Dependencies

Required Python packages (already added to requirements.txt):
- `openpyxl==3.1.2` - Excel file generation
- `reportlab==4.0.4` - PDF file generation

---

## Integration Notes

1. **Unified Endpoint**: Unlike separate API calls, the truck report endpoint returns both summary and detail data in one response, reducing API calls and ensuring data consistency.

2. **Distance Tracking**: The API helps fleet managers identify routes with excessive distance variations, which could indicate:
   - Route deviation issues
   - GPS tracking accuracy
   - Driver behavior patterns

3. **Damage Reporting**: Track which vehicles have reported damage for maintenance planning and insurance tracking.

4. **Export Functionality**: Both Excel and PDF exports include summary statistics for comprehensive reporting to stakeholders.

5. **Performance**: The merged endpoint is optimized to compute statistics while gathering report data, minimizing database queries.
