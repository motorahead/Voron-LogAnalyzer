# Voron Log Analyzer - Quick Start Guide

## What's New in v2

Your analyzer has been enhanced with 11 powerful new features:

### 🎯 Visual Improvements
- **Smart Label Layout** - Milestone labels automatically avoid overlapping
- **Extended Data View** - Graph now shows 15 minutes past print end to capture full cooldown
- **Dual Chart System** - Separate charts for temperatures and system metrics

### ⚙️ Customization Options
- **Configurable Statistics** - Choose which stats to display
- **Time Format Toggle** - Switch between 12-hour (with AM/PM) and 24-hour format
- **Granularity Presets** - Quick buttons for All/High/Med/Low data sampling

### 📊 Enhanced Data
- **Universal Message Parsing** - Now captures echo, respond, and error messages
- **Additional Metrics** - MCU load, task timing, and PWM data
- **System Metrics Chart** - Dedicated chart for MCU, RPi, and toolhead temperatures

## How to Use

### 1. Load Your Logs
- Drag and drop or click to load `klippy.log` (required)
- Optionally load `KlipperScreen.log` for milestone markers
- Click **▶ Analyze Logs**

### 2. Explore Your Data

**Temperature Profile Chart (Top)**
- Shows bed, chamber, and extruder temperatures
- Milestone markers with smart positioning
- Zoom and pan with mouse
- Toggle series on/off in sidebar

**System Metrics Chart (Bottom)**
- MCU, RPi, and toolhead temperatures
- MCU load and task timing metrics
- Independent from temperature chart

### 3. Customize Your View

**Settings Panel:**
- **Data Granularity** - Use presets or slider to control data density
  - All (1): Every data point
  - High (2): Every 2nd point
  - Med (5): Every 5th point
  - Low (10): Every 10th point
- **Time Format** - Choose 12-hour or 24-hour display
- **Milestone Filter** - Filter by category (Print Start, Bed, Chamber, Cooldown, Other)

**Series Toggles:**
- Check/uncheck to show/hide temperature series
- Each series has a color indicator

**System Toggles:**
- Control which system metrics appear in Chart 2
- MCU Temp, RPi Temp, Toolhead Temp
- MCU Load, Task Avg, Bed PWM

### 4. View Statistics

The statistics panel shows:
- Session Duration
- Peak Bed/Chamber/Extruder Temps
- Heatsoak and Cooldown Durations
- Average Chamber/Bed Temps during printing
- Chamber Temperature Stability (standard deviation)

### 5. Export Your Data

**Export Options:**
- 📷 **Chart as PNG** - Save temperature chart as image (1600x800)
- 📷 **Chart 2 as PNG** - Save system metrics chart
- 📊 **Temp data CSV** - Export all temperature data
- 📋 **Milestones CSV** - Export timeline events

## Tips & Tricks

### For Best Results
1. **Load both logs** - KlipperScreen.log adds valuable milestone markers
2. **Use granularity presets** - Start with "Med" for large log files
3. **Filter milestones** - Focus on specific phases (heatsoak, cooldown, etc.)
4. **Compare sessions** - Click different sessions to see how prints vary

### Understanding the Charts

**Milestone Markers:**
- Vertical dotted lines show events
- Labels positioned at different heights to avoid overlap
- Color-coded for easy identification
- Shaded regions show heatsoak (blue) and cooldown (orange) phases

**Temperature Ranges:**
- Left Y-axis: Bed and chamber temps (0-130°C)
- Right Y-axis: Extruder temp (0-310°C)
- System chart: 0-100°C for temps, 0-100% for load

### Troubleshooting

**Graph cuts off early?**
- This is now fixed! Data extends 15 minutes past session end

**Labels overlapping?**
- Smart layout is automatic, but if you have many simultaneous messages, some may still be close

**Missing data?**
- Ensure your klippy.log contains "Stats" lines
- Check that sensor names match (Chamber_Temp, Toolhead_Board, etc.)

**Sessions not showing?**
- Sessions appear after you click "Analyze Logs"
- If no KlipperScreen.log, you'll see one "Full log" session

## File Locations

- **Main analyzer:** `voron_log_analyzer.html`
- **Original backup:** `voron_log_analyzer_backup_20260506_195506.html`
- **Your logs:** Typically in `~/printer_data/logs/` on your printer

## Browser Compatibility

Works best in modern browsers:
- Chrome/Edge (recommended)
- Firefox
- Safari

Requires JavaScript enabled.

## Need Help?

Check these files for more details:
- `VERIFIED_STATUS.md` - Complete feature list and verification
- `IMPLEMENTATION_GUIDE.md` - Technical implementation details
- `ENHANCEMENT_PLAN.md` - Original feature specifications

Enjoy your enhanced log analyzer! 🚀
