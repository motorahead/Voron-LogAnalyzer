# Voron Log Analyzer — Requirements

## Overview
A single-file HTML tool for visualizing Klipper 3D printer logs. Loads `klippy.log` and optionally `KlipperScreen.log`, parses temperature and event data, and renders interactive charts with milestone annotations.

---

## Functional Requirements

### 1. Log Loading
- Load `klippy.log` via file picker or drag-and-drop
- Load `KlipperScreen.log` via file picker or drag-and-drop (optional)
- Show filename and file size after load
- Enable "Analyze" button only when klippy.log is loaded

### 2. Session Detection & Separation
- Detect individual print jobs from KlipperScreen job state transitions (`standby → printing → complete/ready`)
- Each job is a separate selectable session
- Sessions are listed by filename and start time
- Selecting a session scopes all charts, stats, and milestone table to that job
- "All Sessions" view shows the full log with session boundary markers
- Ctrl+Click to select multiple sessions for comparison
- When no KlipperScreen log is loaded, treat the full log as one session

### 3. Chart 1 — Print Job & Temperature Profile
Displays data specific to the selected print job:
- **Bed temperature** (actual + target)
- **Chamber temperature**
- **Extruder temperature** (actual + target)
- **Milestone annotations** from KlipperScreen echo/respond/error messages
- **Phase shading**: heatsoak region (blue tint), cooldown region (amber tint)
- **Session boundary lines** when viewing all sessions (green = start, red = end)
- All series are individually toggleable via sidebar checkboxes
- Data extends 15 minutes past session end to capture full cooldown

### 4. Chart 2 — System & Performance Metrics
Displays hardware and system data for the selected session:
- **MCU temperature**
- **Raspberry Pi temperature**
- **Toolhead board temperature**
- **MCU load** (`mcu_awake` as percentage)
- **Task average timing** (`mcu_task_avg` in milliseconds)
- **Bed heater PWM** (`heater_bed pwm` as percentage)
- All metrics are individually toggleable via sidebar checkboxes
- Shares the same time axis as Chart 1

### 5. Selectable Metrics (Filters)
- Every data series in both charts has a toggle checkbox in the sidebar
- Chart 1 series grouped under "Temperature Series"
- Chart 2 metrics grouped under "Performance Metrics"
- Toggling a series immediately re-renders the relevant chart

### 6. Session Statistics
- Displayed above Chart 1 after parsing
- Each stat is individually show/hide configurable via "⚙️ Configure" button
- Available stats:
  - Session Duration
  - Peak Bed Temperature
  - Peak Chamber Temperature
  - Max Extruder Temperature
  - Heatsoak Duration (start → complete)
  - Cooldown Duration (start → complete)
  - Average Chamber Temp (during active printing)
  - Average Bed Temp (during active printing)
  - Chamber Temperature Stability (standard deviation)

### 7. Milestone Timeline Table
- Lists all KlipperScreen messages in chronological order
- Columns: Time, +min (offset from session start), Type (echo/respond/error), Category, Message
- Filterable by category: All, Print Start, Bed, Chamber, Cooldown, Echo, Respond, Error, Other
- Color-coded type badges
- Exportable as CSV

### 8. Milestone Annotations on Chart
- Vertical dotted lines at each milestone time
- Text labels with smart positioning to prevent overlap
- Labels grouped into clusters (events within 5 minutes)
- Up to 10 vertical Y-levels to stagger overlapping labels
- Horizontal offset applied within clusters
- Toggle labels on/off (lines remain visible)
- In "All Sessions" view, only key milestones shown (max 25)
- In single session view, up to 50 milestones shown

### 9. Message Parsing
- Parse three KlipperScreen message types:
  - `echo:` — M118 output
  - `// ` — RESPOND command output
  - `!! ` — Error messages
- Each type gets a distinct color badge in the milestone table
- All types appear as annotations on Chart 1

### 10. Settings
- **Data Granularity**: slider 1–30 with presets (All=1, High=2, Med=5, Low=10). Controls every Nth data point rendered — higher = faster for large files.
- **Time Format**: 12-hour (AM/PM) or 24-hour toggle. Applies to chart axes and milestone table.
- **Show Milestone Labels**: checkbox to toggle annotation text on Chart 1 (lines remain).
- **Milestone Category Filter**: dropdown to filter milestone table and chart annotations by category.

### 11. Export
- Export Chart 1 as PNG (1600×800)
- Export Chart 2 as PNG (1600×800)
- Export temperature data as CSV (time, all temp channels)
- Export milestone timeline as CSV

---

## Non-Functional Requirements

- **Single file**: entire tool is one self-contained `.html` file, no server required
- **Offline capable**: only external dependency is Plotly.js CDN
- **Performance**: granularity control keeps rendering fast for logs > 10MB
- **Dark theme**: consistent dark UI (#0d1117 background)
- **Responsive**: sidebar + main content layout, charts resize with window

---

## Known Limitations

- Annotation labels are smart-positioned but not manually draggable
- Files > 50MB may be slow at granularity=1; use Med or Low preset
- Requires a modern browser (Chrome, Firefox, Edge)
- Cooldown duration shows "—" if no "cooldown complete" message exists in log

---

## Data Sources

### klippy.log — Stats lines
Parsed fields per `Stats X.X:` line:
| Field | Regex | Unit |
|-------|-------|------|
| Bed temp/target | `heater_bed: target=X temp=X` | °C |
| Chamber temp | `Chamber_Temp: temp=X` | °C |
| Extruder temp/target | `extruder: target=X temp=X` | °C |
| Toolhead board temp | `Toolhead_Board: temp=X` | °C |
| MCU temp | `MCU: temp=X` | °C |
| RPi temp | `RaspberryPi: temp=X` | °C |
| MCU load | `mcu_awake=X` | % (×100) |
| Task avg | `mcu_task_avg=X` | ms (×1000) |
| Bed PWM | `heater_bed:.*pwm=X` | % |

### KlipperScreen.log — Event lines
| Event | Pattern |
|-------|---------|
| Echo message | `[screen.py:show_popup_message()] - echo: MSG` |
| Respond message | `[screen.py:show_popup_message()] - // MSG` |
| Error message | `[screen.py:show_popup_message()] - !! MSG` |
| Job state change | `[job_status.py:set_state()] - Changing job_status state from 'X' to 'Y'` |
| Filename update | `[job_status.py:update_filename()] - Updating filename to FILE` |
