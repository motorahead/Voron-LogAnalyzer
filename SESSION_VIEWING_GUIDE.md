# Session Viewing Guide

## Three Viewing Modes

### 1. 📊 All Sessions Mode
**How to activate:** Click "All Sessions" at the top of the session list

**What it shows:**
- Complete log data from start to finish
- All temperature readings across all prints
- Visual markers for each print session:
  - 🟢 Green vertical line = Print start
  - 🔴 Red vertical line = Print end
  - Session name label at top of each print

**Use cases:**
- Overview of all printing activity
- Identify patterns across multiple prints
- See gaps between prints
- Monitor overall printer behavior

### 2. 🎯 Single Session Mode
**How to activate:** Click any individual session in the list

**What it shows:**
- Focused view of one print session
- 2 minutes before print start
- Full print duration
- Complete cooldown (extends automatically)
- 5 minutes after cooldown completes

**Use cases:**
- Detailed analysis of a specific print
- Troubleshooting a particular job
- Examining heatsoak and cooldown behavior

### 3. 🔀 Multi-Select Mode
**How to activate:** Hold Ctrl (Windows/Linux) or Cmd (Mac) and click multiple sessions

**What it shows:**
- Combined view of selected sessions only
- Each session with its own markers
- Allows comparison of specific prints

**Use cases:**
- Compare similar prints
- Analyze differences between successful/failed prints
- Study how settings changes affect results

## Visual Indicators

### Temperature Traces
- **Red solid line** - Bed temperature
- **Red dashed line** - Bed target temperature
- **Blue solid line** - Chamber temperature
- **Orange solid line** - Extruder temperature

### Phase Markers
- **Blue shaded area** - Heatsoak phase (chamber warming)
- **Orange shaded area** - Cooldown phase (active cooling)

### Session Markers (All Sessions / Multi-Select only)
- **Green vertical line** - Print start time
- **Red vertical line** - Print end time
- **Green label** - Session/filename at top

### Milestone Markers
- **Colored dotted lines** - Echo messages from KlipperScreen
- **Small labels** - Message text (smart positioned to avoid overlap)

## Statistics Panel

Shows aggregate stats for the current view:
- **Single session:** Stats for that session only
- **All sessions:** Stats across entire log
- **Multi-select:** Combined stats for selected sessions

Available statistics:
- Session Duration
- Peak Bed/Chamber/Extruder Temps
- Heatsoak Duration
- Cooldown Duration
- Average Chamber/Bed Temps (during printing)
- Temperature Stability (standard deviation)

## Tips

### For Best Results
1. **Start with All Sessions** to get an overview
2. **Click individual sessions** to investigate specific prints
3. **Use Ctrl+Click** to compare 2-3 similar prints
4. **Adjust granularity** if the graph is slow (use Med or Low for large logs)

### Understanding Cooldown Duration
- Cooldown starts when print ends or when "Cooldown:" messages appear
- Cooldown ends with "cooldown complete" message
- Duration shown is the actual time spent cooling
- Graph extends to show full cooldown data

### Session Detection
- Sessions are auto-detected from KlipperScreen job status changes
- If no KlipperScreen.log, you'll see one "Full log" session
- Sessions show the actual print filename when available

## Troubleshooting

**Graph cuts off early?**
- Fixed! Graph now extends through full cooldown automatically

**Cooldown duration shows 0 min?**
- Fixed! Now correctly finds matching start/end pairs

**Labels overlapping?**
- Smart layout algorithm positions them automatically
- Some overlap may occur with many simultaneous messages

**Can't see all sessions?**
- Make sure you clicked "All Sessions" at the top
- Check that both log files loaded successfully

**Multi-select not working?**
- Hold Ctrl (or Cmd on Mac) while clicking
- Look for the hint text at bottom of session list
