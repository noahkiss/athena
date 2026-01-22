---
# pkms-3len
title: Add dashboard with stats and visualizations
status: draft
type: feature
created_at: 2026-01-22T02:41:24Z
updated_at: 2026-01-22T02:41:24Z
---

Create a dashboard showing notes captured, category distribution, streaks, and atlas growth over time.

## Metrics to Display
- Notes captured: today, this week, this month, all time
- Category breakdown: pie chart or bar chart
- Capture streak: days in a row with at least one note
- Atlas growth: line chart showing notes over time
- Most active categories
- Recent activity feed

## Design
- New /dashboard route
- Card-based layout (responsive grid)
- Simple charts using Chart.js or similar lightweight library
- Mobile-friendly visualizations

## Technical Notes
- Query git history for historical data
- Cache calculations (don't recompute on every load)
- Use SQLite state DB for fast queries
- Progressive enhancement (works without JS)

## Checklist
- [ ] Design dashboard layout (wireframe)
- [ ] Choose charting library (Chart.js, Recharts, or D3 minimal)
- [ ] Add /dashboard route to Scribe
- [ ] Implement API endpoint for dashboard stats
- [ ] Build stats cards (notes captured, streaks, etc.)
- [ ] Add category distribution chart
- [ ] Add atlas growth timeline chart
- [ ] Add recent activity feed
- [ ] Make responsive for mobile
- [ ] Add to main navigation
- [ ] Cache stats calculations