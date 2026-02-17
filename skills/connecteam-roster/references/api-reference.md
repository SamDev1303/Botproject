# Connecteam API Reference

## Auth
- **Header:** `X-API-KEY: <api_key>`
- **Base URL:** `https://api.connecteam.com`
- **AU Base URL:** `https://api-au.connecteam.com` (not working for this account — use global)
- **API Key env var:** `CONNECTEAM_API_ID`

## Scheduler ID
- **Clean Up Bros Schedule:** `13218868`
- **Timezone:** `Australia/Sydney`

## Staff (User IDs)
| Name | userId | Role | Phone |
|------|--------|------|-------|
| Hafsah Nuzhat | 11925732 | Owner | +61406764585 |
| Shamal Krishna | 11925807 | Manager | +61451449770 |
| Teenay Josh | 13917939 | Worker | +61413389943 |

## Jobs (Locations)
| Job | jobId | Code | Address |
|-----|-------|------|---------|
| AIRBNB (Unit 3) | d727a2b8-f8f8-4538-9cbc-935e715c7551 | UNIT3 | 330 Atkinson St, Liverpool NSW 2170 |
| AIRBNB 2 (Unit 4) | 9f160c27-bb7e-472e-a34e-5acd8d814b11 | UNIT4 | 330 Atkinson St, Liverpool NSW 2170 |
| AIRBNB 3 (Unit 2) | 3fb04448-8f46-464d-9655-d92076923223 | UNIT 2 NIGAL | Unit 2 Nigal St, Liverpool |
| HOME | 05ea4cab-0b64-b678-18e4-d383ae3235d2 | HOME SITE | 41 Wonga Rd, Lurnea NSW 2170 |

## Endpoints

### Account
- `GET /me` — Company info

### Users
- `GET /users/v1/users` — List all staff
- `GET /users/v1/users?userId=<id>` — Get specific user

### Schedulers
- `GET /scheduler/v1/schedulers` — List all schedulers

### Shifts (CRUD)
- `GET /scheduler/v1/schedulers/{schedulerId}/shifts?startTime={unix}&endTime={unix}` — List shifts in date range
- `GET /scheduler/v1/schedulers/{schedulerId}/shifts/{shiftId}` — Get single shift
- `POST /scheduler/v1/schedulers/{schedulerId}/shifts` — Create shift(s)
- `PUT /scheduler/v1/schedulers/{schedulerId}/shifts/{shiftId}` — Update shift
- `DELETE /scheduler/v1/schedulers/{schedulerId}/shifts/{shiftId}` — Delete shift

### Jobs (Locations/Roles)
- `GET /jobs/v1/jobs` — List all jobs
- `GET /jobs/v1/jobs/{jobId}` — Get single job
- `POST /jobs/v1/jobs` — Create job(s)
- `PUT /jobs/v1/jobs/{jobId}` — Update job
- `DELETE /jobs/v1/jobs/{jobId}` — Delete job

## Shift Object (Create/Update)
```json
{
  "shifts": [
    {
      "title": "End of Lease Clean",
      "startTime": 1736924400,
      "endTime": 1736942400,
      "timezone": "Australia/Sydney",
      "assignedUserIds": [13917939],
      "jobId": "d727a2b8-f8f8-4538-9cbc-935e715c7551",
      "isPublished": true,
      "notes": [{"text": "3BR house, bring all supplies"}],
      "allDay": false,
      "isOpenShift": false
    }
  ]
}
```

## Shift Fields
| Field | Type | Description |
|-------|------|-------------|
| title | string | Shift name |
| startTime | int | Unix timestamp |
| endTime | int | Unix timestamp |
| timezone | string | e.g. "Australia/Sydney" |
| assignedUserIds | array[int] | Staff user IDs |
| jobId | string | Job/location ID |
| isPublished | bool | Visible to staff |
| notes | array | `[{"text": "..."}]` |
| allDay | bool | All-day shift |
| isOpenShift | bool | Open for claiming |
| color | string | Hex color |

## Pagination
- List endpoints return `paging.offset`
- Use `?offset=N&limit=N` for pagination

## Rate Limits
- Per plan. Check `X-RateLimit-*` headers.
