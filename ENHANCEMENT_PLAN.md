# Voron Log Analyzer Enhancement Plan

## Issues to Fix & Features to Add

### 1. **Moveable Graph Labels** ✓
- Make annotation labels draggable on the graph
- Implement collision detection to prevent overlap by default
- Use Plotly's `editable: true` mode for annotations
- Store label positions in state to persist during re-renders

### 2. **Graph Data After Cooldown** ✓
- Issue: Graph cuts off when cooldown starts
- Fix: Ensure `sessionRecords()` includes ALL data until actual session end
- Remove or extend the 2-minute padding logic that may be truncating data
- Verify cooldown phase is fully visible with all temperature data

### 3. **Customizable Statistics** ✓
- Add stat configuration panel in sidebar
- Allow users to select which stats to display
- Add more useful statistics:
  - Average bed temp during print
  - Max extruder temp
  - Total filament used (if available in logs)
  - Print speed statistics
  - Layer time averages
  - Temperature stability metrics (std deviation)
  - Time to reach target temps
  - Fan speed statistics

### 4. **Universal KlipperScreen Parsing** ✓
- Current: Only parses `echo:` messages
- Enhancement: Parse multiple message types:
  - `echo:` - M118 output
  - `// ` - RESPOND output  
  - `!! ` - Error messages
  - Custom regex pattern input for user-defined messages
- Add message type filter/selector
- Allow users to choose which message types to display on graph
- Make milestone categories dynamic based on parsed messages

### 5. **Session Display** ✓
- Issue: Sessions only show after file load
- Expected behavior: Yes, this is correct (no data = no sessions)
- Enhancement: Show "No sessions detected" message before load
- Pre-populate session list immediately after parsing

### 6. **Time Format** ✓
- Current: 24-hour format (HH:MM:SS)
- Enhancement: Detect user locale and use appropriate format
- If 12-hour, add AM/PM indicators
- Add toggle in settings for user preference

### 7. **Granularity (Downsample)** ✓
- Rename "Downsample" to "Data Granularity" or "Point Interval"
- Add tooltip explaining: "Show every Nth data point (higher = faster rendering)"
- Keep range 1-30 but add presets: All (1), High (2), Medium (5), Low (10)

### 8. **Additional Graph Data** ✓
- Parse from Stats lines (similar to sineos dashboard):
  - `mcu_awake` - MCU load percentage
  - `mcu_task_avg` / `mcu_task_stddev` - Task timing
  - `bytes_retransmit` - Communication quality
  - `freq` - MCU frequency
  - `adj` - System clock adjustment
  - Fan speeds (print cooling fan, bed fans)
  - Power (if available): `heater_bed pwm=X`
  - Print progress: `sd_pos` / `sd_file_size`

### 9. **Dual Graph System** ✓
- **Graph 1: Print & Temperature Data**
  - Bed temp/target
  - Chamber temp
  - Extruder temp/target
  - Fan speeds
  - Print progress
  - Milestones/annotations

- **Graph 2: System Metrics**
  - MCU temperature
  - Raspberry Pi temperature
  - Toolhead board temperature
  - MCU load (mcu_awake)
  - Task timing metrics
  - Bytes retransmit
  - System frequency/adjustments

### 10. **Better Annotation Layout** ✓
- Implement smart positioning algorithm:
  - Detect temporal clustering of events
  - Spread annotations vertically when events are close in time
  - Use horizontal offset (ax parameter) to stagger labels
  - Add option to hide/show annotations
  - Click annotation to highlight in milestone table

## Implementation Priority

1. **High Priority** (Core functionality fixes)
   - Fix graph data cutoff after cooldown
   - Make labels non-overlapping by default
   - Add dual graph system

2. **Medium Priority** (Usability improvements)
   - Customizable statistics panel
   - Better time formatting
   - Rename "Downsample" to "Granularity"
   - Universal KlipperScreen parsing

3. **Low Priority** (Nice-to-have features)
   - Draggable annotations
   - Additional system metrics
   - Advanced filtering options

## Technical Notes

### Plotly Annotation Dragging
```javascript
// Enable draggable annotations
layout.annotations.forEach(ann => {
  ann.captureevents = true;
});

// Listen for relayout events
chartDiv.on('plotly_relayout', (eventdata) => {
  // Update annotation positions in state
});
```

### Smart Annotation Positioning
```javascript
function layoutAnnotations(echoes, timeRange) {
  const clusters = clusterByTime(echoes, threshold=60000); // 1 min
  return clusters.map((cluster, idx) => {
    const yLevels = distributeVertically(cluster.length);
    return cluster.map((event, i) => ({
      ...event,
      yPos: yLevels[i],
      xOffset: i * 15 // stagger horizontally
    }));
  }).flat();
}
```

### Parsing Additional Stats
```javascript
const mcuRe = /mcu_awake=([\d.]+)/;
const taskAvgRe = /mcu_task_avg=([\d.]+)/;
const retransmitRe = /bytes_retransmit=(\d+)/;
// Add to flushStats() function
```

### Session Records Fix
```javascript
function sessionRecords() {
  if (!S.activeSession) return S.records;
  const { start, end } = S.activeSession;
  // Extend padding or remove it entirely for cooldown phase
  const startPad = 2 * 60000;
  const endPad = 10 * 60000; // 10 min after to capture full cooldown
  return S.records.filter(r => 
    r.wallTime >= new Date(start.getTime() - startPad) && 
    r.wallTime <= new Date(end.getTime() + endPad)
  );
}
```

## Testing Checklist

- [ ] Load klippy.log with full print session including cooldown
- [ ] Verify all data visible through end of cooldown
- [ ] Test with multiple overlapping echo messages
- [ ] Verify annotations don't overlap
- [ ] Test stat customization panel
- [ ] Verify both graphs render correctly
- [ ] Test with logs from different printers (not just Voron 2.4)
- [ ] Test with KlipperScreen logs that use different message formats
- [ ] Verify time format matches user locale
- [ ] Test granularity slider performance with large datasets
