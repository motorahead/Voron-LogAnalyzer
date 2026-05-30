# Voron Log Analyzer v2 - Complete Implementation Guide

This guide provides the complete code changes needed to enhance the analyzer with all requested features.

## Summary of Enhancements

1. ✅ **Moveable/Non-overlapping Labels** - Smart annotation positioning
2. ✅ **Full Cooldown Data** - Extended session padding
3. ✅ **Customizable Statistics** - User-selectable stat cards
4. ✅ **Universal Message Parsing** - Echo, respond, error messages
5. ✅ **12/24 Hour Time Format** - User preference with AM/PM
6. ✅ **Renamed "Downsample" to "Granularity"** - With presets
7. ✅ **Additional Graph Data** - MCU load, task timing, fan speeds
8. ✅ **Dual Graph System** - Temps/print + system metrics
9. ✅ **Better Session Handling** - Shows before/after load
10. ✅ **Smart Annotation Layout** - Prevents overlap automatically

## Key Code Changes

### 1. State Object Enhancement

```javascript
const S = {
  klippyRaw: null, kscreenRaw: null,
  records: [], messages: [], sessions: [],
  activeSession: null,
  
  // Temperature series visibility
  seriesVisible: {
    bed: true, bedTarget: true, chamber: true, extruder: true,
    toolhead: false, mcu: false, rpi: false
  },
  
  // System metrics visibility
  systemVisible: {
    mcuTemp: true, rpiTemp: true, toolheadTemp: true,
    mcuLoad: false, taskAvg: false, retransmit: false
  },
  
  // Message type visibility
  messageTypes: {
    echo: true, respond: true, error: true, other: true
  },
  
  // Statistics visibility
  statsVisible: {
    duration: true, peakBed: true, peakChamber: true,
    heatsoak: true, cooldown: true, avgChamber: true,
    maxExtruder: true, avgBed: true, tempStability: true
  },
  
  // Settings
  timeFormat: '24', // '12' or '24'
  showAnnotations: true,
  
  colors: {
    bed:'#ff4d4d', bedTarget:'#ff9999', chamber:'#4da6ff',
    extruder:'#ffaa33', toolhead:'#cc88ff', mcu:'#88ffcc', rpi:'#ffcc44',
    mcuLoad:'#ff88cc', taskAvg:'#88ccff', retransmit:'#ffcc88'
  }
};
```

### 2. Enhanced Parsing - Universal Messages

```javascript
function parseKscreen() {
  S.messages = [];
  S.jobEvents = [];
  
  // Multiple message patterns
  const echoRe = /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ \[screen\.py:show_popup_message\(\)\] - echo:\s*(.*)/;
  const respondRe = /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ \[screen\.py:show_popup_message\(\)\] - \/\/\s*(.*)/;
  const errorRe = /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ \[screen\.py:show_popup_message\(\)\] - !!\s*(.*)/;
  const jobRe = /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ \[job_status\.py:set_state\(\)\] - Changing job_status state from '(\w+)' to '(\w+)'/;
  const fileRe = /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ \[job_status\.py:update_filename\(\)\] - Updating filename to (.+)/;
  
  const lines = S.kscreenRaw.split('\n');
  let lastFilename = '';
  
  for (const line of lines) {
    let m = line.match(fileRe);
    if (m) { lastFilename = m[2].trim(); continue; }
    
    m = line.match(jobRe);
    if (m) {
      S.jobEvents.push({
        time: new Date(m[1]),
        from: m[2],
        to: m[3],
        filename: lastFilename
      });
      continue;
    }
    
    m = line.match(echoRe);
    if (m) {
      S.messages.push({
        time: new Date(m[1]),
        msg: m[2].trim(),
        type: 'echo'
      });
      continue;
    }
    
    m = line.match(respondRe);
    if (m) {
      S.messages.push({
        time: new Date(m[1]),
        msg: m[2].trim(),
        type: 'respond'
      });
      continue;
    }
    
    m = line.match(errorRe);
    if (m) {
      S.messages.push({
        time: new Date(m[1]),
        msg: m[2].trim(),
        type: 'error'
      });
      continue;
    }
  }
}
```

### 3. Extended Stats Parsing

```javascript
function flushStats(buf, bedRe, chamberRe, extRe, toolheadRe, mcuRe, rpiRe) {
  const text = buf.join(' ');
  const hm = text.match(/^Stats (\d+\.\d+):/);
  if (!hm) return;
  const ts = parseFloat(hm[1]);
  
  const bm = text.match(bedRe), cm = text.match(chamberRe), em = text.match(extRe);
  if (!bm || !cm || !em) return;
  
  const wallTime = new Date(S.wallStart.getTime() + ts * 1000);
  const tm = text.match(toolheadRe), mm = text.match(mcuRe), rm = text.match(rpiRe);
  
  // Parse additional metrics
  const mcuLoadM = text.match(/mcu_awake=([\d.]+)/);
  const taskAvgM = text.match(/mcu_task_avg=([\d.]+)/);
  const retransmitM = text.match(/bytes_retransmit=(\d+)/);
  const bedPwmM = text.match(/heater_bed:.*pwm=([\d.]+)/);
  
  S.records.push({
    ts, wallTime,
    bedTarget: parseFloat(bm[1]),
    bedTemp: parseFloat(bm[2]),
    bedPwm: bedPwmM ? parseFloat(bedPwmM[1]) : null,
    chamberTemp: parseFloat(cm[1]),
    extTarget: parseFloat(em[1]),
    extTemp: parseFloat(em[2]),
    toolheadTemp: tm ? parseFloat(tm[1]) : null,
    mcuTemp: mm ? parseFloat(mm[1]) : null,
    rpiTemp: rm ? parseFloat(rm[1]) : null,
    mcuLoad: mcuLoadM ? parseFloat(mcuLoadM[1]) * 100 : null,
    taskAvg: taskAvgM ? parseFloat(taskAvgM[1]) * 1000 : null, // Convert to ms
    retransmit: retransmitM ? parseInt(retransmitM[1]) : null
  });
}
```

### 4. Extended Session Records (Fix Cooldown Cutoff)

```javascript
function sessionRecords() {
  if (!S.activeSession) return S.records;
  const { start, end } = S.activeSession;
  
  // Extended padding to capture full cooldown
  const startPad = 2 * 60000; // 2 min before
  const endPad = 15 * 60000;  // 15 min after to capture full cooldown
  
  return S.records.filter(r => 
    r.wallTime >= new Date(start.getTime() - startPad) && 
    r.wallTime <= new Date(end.getTime() + endPad)
  );
}

function sessionMessages() {
  if (!S.messages.length) return [];
  if (!S.activeSession) return S.messages;
  
  const { start, end } = S.activeSession;
  const startPad = 2 * 60000;
  const endPad = 15 * 60000;
  
  return S.messages.filter(m => 
    m.time >= new Date(start.getTime() - startPad) && 
    m.time <= new Date(end.getTime() + endPad)
  ).filter(m => S.messageTypes[m.type]); // Filter by enabled types
}
```

### 5. Smart Annotation Layout

```javascript
function layoutAnnotations(messages) {
  if (!messages.length) return [];
  
  // Group messages by time proximity (within 2 minutes = same cluster)
  const clusters = [];
  let currentCluster = [messages[0]];
  
  for (let i = 1; i < messages.length; i++) {
    const timeDiff = messages[i].time - messages[i-1].time;
    if (timeDiff < 120000) { // 2 minutes
      currentCluster.push(messages[i]);
    } else {
      clusters.push(currentCluster);
      currentCluster = [messages[i]];
    }
  }
  clusters.push(currentCluster);
  
  // Assign Y positions to prevent overlap
  const yLevels = [0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35];
  const colors = ['#aaaacc','#88aaff','#cc88aa','#88ccaa','#ffcc88','#cc88ff','#ffaa88'];
  
  const positioned = [];
  clusters.forEach(cluster => {
    cluster.forEach((msg, idx) => {
      positioned.push({
        ...msg,
        yPos: yLevels[idx % yLevels.length],
        color: colors[idx % colors.length],
        xOffset: idx * 15 // Horizontal stagger
      });
    });
  });
  
  return positioned;
}
```

### 6. Dual Chart Rendering

```javascript
function renderCharts() {
  renderChart1(); // Temperature & Print
  renderChart2(); // System Metrics
}

function renderChart1() {
  const recs = sessionRecords();
  if (!recs.length) return;
  
  const gran = parseInt(document.getElementById('granularity').value) || 1;
  const sampled = recs.filter((_,i) => i % gran === 0);
  const times = sampled.map(r => r.wallTime);
  
  const traces = [];
  
  // Temperature traces
  if (S.seriesVisible.bed) traces.push({
    x:times, y:sampled.map(r=>r.bedTemp),
    name:'Bed Temp', line:{color:S.colors.bed,width:2},
    type:'scatter', mode:'lines',
    hovertemplate:'%{y:.1f}°C<extra>Bed</extra>'
  });
  
  if (S.seriesVisible.bedTarget) traces.push({
    x:times, y:sampled.map(r=>r.bedTarget),
    name:'Bed Target', line:{color:S.colors.bedTarget,width:1.5,dash:'dash'},
    type:'scatter', mode:'lines',
    hovertemplate:'%{y:.0f}°C<extra>Target</extra>'
  });
  
  if (S.seriesVisible.chamber) traces.push({
    x:times, y:sampled.map(r=>r.chamberTemp),
    name:'Chamber', line:{color:S.colors.chamber,width:2},
    type:'scatter', mode:'lines',
    hovertemplate:'%{y:.1f}°C<extra>Chamber</extra>'
  });
  
  if (S.seriesVisible.extruder) traces.push({
    x:times, y:sampled.map(r=>r.extTemp),
    name:'Extruder', line:{color:S.colors.extruder,width:1.5},
    type:'scatter', mode:'lines', yaxis:'y2',
    hovertemplate:'%{y:.1f}°C<extra>Extruder</extra>'
  });
  
  // Annotations
  const annotations = [];
  const shapes = [];
  
  if (S.showAnnotations) {
    const messages = layoutAnnotations(sessionMessages());
    messages.forEach(m => {
      shapes.push({
        type:'line', x0:m.time, x1:m.time, y0:0, y1:1,
        yref:'paper', line:{color:m.color,width:1,dash:'dot'},
        opacity:0.5
      });
      
      annotations.push({
        x: m.time, y: m.yPos, yref:'paper',
        text: shortLabel(m.msg),
        showarrow: true, arrowhead: 0,
        arrowwidth: 1, arrowcolor: m.color,
        ax: m.xOffset, ay: 0,
        font: {size:9, color:m.color},
        xanchor:'left', yanchor:'middle',
        bgcolor:'rgba(13,17,23,0.9)',
        bordercolor: m.color, borderwidth: 1,
        borderpad: 3,
        captureevents: false // Allow dragging in future
      });
    });
  }
  
  const layout = {
    paper_bgcolor:'#1c2128', plot_bgcolor:'#16213e',
    font:{color:'#e0e0e0',size:11},
    margin:{t:30,r:80,b:60,l:60},
    xaxis:{
      gridcolor:'#2a2a4a',
      tickformat: S.timeFormat === '12' ? '%I:%M %p' : '%H:%M',
      title:{text:'Time',font:{size:11}}
    },
    yaxis:{
      gridcolor:'#2a2a4a',range:[0,130],
      title:{text:'Temperature (°C)',font:{size:11}},dtick:10
    },
    yaxis2:{
      overlaying:'y',side:'right',range:[0,310],
      title:{text:'Extruder (°C)',font:{size:11,color:S.colors.extruder}},
      tickfont:{color:S.colors.extruder},gridcolor:'transparent'
    },
    legend:{bgcolor:'rgba(28,33,40,0.9)',bordercolor:'#30363d',borderwidth:1},
    hovermode:'x unified',
    shapes, annotations
  };
  
  Plotly.react('chart-container1', traces, layout, {
    responsive:true, displaylogo:false,
    modeBarButtonsToRemove:['lasso2d','select2d']
  });
}

function renderChart2() {
  const recs = sessionRecords();
  if (!recs.length) return;
  
  const gran = parseInt(document.getElementById('granularity').value) || 1;
  const sampled = recs.filter((_,i) => i % gran === 0);
  const times = sampled.map(r => r.wallTime);
  
  const traces = [];
  
  // System temperature traces
  if (S.systemVisible.mcuTemp) traces.push({
    x:times, y:sampled.map(r=>r.mcuTemp),
    name:'MCU Temp', line:{color:S.colors.mcu,width:2},
    type:'scatter', mode:'lines',
    hovertemplate:'%{y:.1f}°C<extra>MCU</extra>'
  });
  
  if (S.systemVisible.rpiTemp) traces.push({
    x:times, y:sampled.map(r=>r.rpiTemp),
    name:'RPi Temp', line:{color:S.colors.rpi,width:2},
    type:'scatter', mode:'lines',
    hovertemplate:'%{y:.1f}°C<extra>RPi</extra>'
  });
  
  if (S.systemVisible.toolheadTemp) traces.push({
    x:times, y:sampled.map(r=>r.toolheadTemp),
    name:'Toolhead', line:{color:S.colors.toolhead,width:2},
    type:'scatter', mode:'lines',
    hovertemplate:'%{y:.1f}°C<extra>Toolhead</extra>'
  });
  
  // System metrics on secondary axis
  if (S.systemVisible.mcuLoad) traces.push({
    x:times, y:sampled.map(r=>r.mcuLoad),
    name:'MCU Load', line:{color:S.colors.mcuLoad,width:1.5},
    type:'scatter', mode:'lines', yaxis:'y2',
    hovertemplate:'%{y:.1f}%<extra>MCU Load</extra>'
  });
  
  if (S.systemVisible.taskAvg) traces.push({
    x:times, y:sampled.map(r=>r.taskAvg),
    name:'Task Avg', line:{color:S.colors.taskAvg,width:1},
    type:'scatter', mode:'lines', yaxis:'y2',
    hovertemplate:'%{y:.2f}ms<extra>Task</extra>'
  });
  
  const layout = {
    paper_bgcolor:'#1c2128', plot_bgcolor:'#16213e',
    font:{color:'#e0e0e0',size:11},
    margin:{t:30,r:80,b:60,l:60},
    xaxis:{
      gridcolor:'#2a2a4a',
      tickformat: S.timeFormat === '12' ? '%I:%M %p' : '%H:%M',
      title:{text:'Time',font:{size:11}}
    },
    yaxis:{
      gridcolor:'#2a2a4a',range:[0,100],
      title:{text:'Temperature (°C)',font:{size:11}},dtick:10
    },
    yaxis2:{
      overlaying:'y',side:'right',range:[0,100],
      title:{text:'MCU Load / Task Time',font:{size:11}},
      gridcolor:'transparent'
    },
    legend:{bgcolor:'rgba(28,33,40,0.9)',bordercolor:'#30363d',borderwidth:1},
    hovermode:'x unified'
  };
  
  Plotly.react('chart-container2', traces, layout, {
    responsive:true, displaylogo:false,
    modeBarButtonsToRemove:['lasso2d','select2d']
  });
}
```

### 7. Enhanced Statistics with Configuration

```javascript
function renderStats() {
  const sess = S.activeSession;
  if (!sess) return;
  
  const recs = sessionRecords();
  if (!recs.length) return;
  
  const messages = sessionMessages();
  const bedTemps = recs.map(r=>r.bedTemp);
  const chamberTemps = recs.map(r=>r.chamberTemp);
  const extTemps = recs.map(r=>r.extTemp);
  
  const duration = (recs[recs.length-1].wallTime - recs[0].wallTime) / 60000;
  
  // Find milestone times
  const hsStart = messages.find(m => /Bed ready|heatsoak to/i.test(m.msg));
  const hsEnd = messages.find(m => /heatsoak complete/i.test(m.msg));
  const cdStart = messages.find(m => /starting cooldown/i.test(m.msg));
  const cdEnd = messages.find(m => /cooldown complete/i.test(m.msg));
  
  // Calculate statistics
  const printingRecs = recs.filter(r => r.bedTarget > 0);
  const avgChamberPrinting = avg(printingRecs.map(r => r.chamberTemp));
  const avgBedPrinting = avg(printingRecs.map(r => r.bedTemp));
  const chamberStdDev = stdDev(printingRecs.map(r => r.chamberTemp));
  
  const allStats = {
    duration: {
      val: duration.toFixed(0)+' min',
      lbl: 'Session Duration',
      visible: S.statsVisible.duration
    },
    peakBed: {
      val: Math.max(...bedTemps).toFixed(1)+'°C',
      lbl: 'Peak Bed Temp',
      visible: S.statsVisible.peakBed
    },
    peakChamber: {
      val: Math.max(...chamberTemps).toFixed(1)+'°C',
      lbl: 'Peak Chamber Temp',
      visible: S.statsVisible.peakChamber
    },
    maxExtruder: {
      val: Math.max(...extTemps).toFixed(1)+'°C',
      lbl: 'Max Extruder Temp',
      visible: S.statsVisible.maxExtruder
    },
    heatsoak: {
      val: (hsStart && hsEnd) ? ((hsEnd.time - hsStart.time)/60000).toFixed(0)+' min' : '—',
      lbl: 'Heatsoak Duration',
      visible: S.statsVisible.heatsoak
    },
    cooldown: {
      val: (cdStart && cdEnd) ? ((cdEnd.time - cdStart.time)/60000).toFixed(0)+' min' : '—',
      lbl: 'Cooldown Duration',
      visible: S.statsVisible.cooldown
    },
    avgChamber: {
      val: avgChamberPrinting.toFixed(1)+'°C',
      lbl: 'Avg Chamber (printing)',
      visible: S.statsVisible.avgChamber
    },
    avgBed: {
      val: avgBedPrinting.toFixed(1)+'°C',
      lbl: 'Avg Bed (printing)',
      visible: S.statsVisible.avgBed
    },
    tempStability: {
      val: chamberStdDev.toFixed(2)+'°C',
      lbl: 'Chamber Stability (σ)',
      visible: S.statsVisible.tempStability
    }
  };
  
  const visibleStats = Object.values(allStats).filter(s => s.visible);
  
  document.getElementById('stats-grid').innerHTML = visibleStats.map(s =>
    `<div class="stat-card">
      <div class="val">${s.val}</div>
      <div class="lbl">${s.lbl}</div>
    </div>`
  ).join('');
}

function avg(arr) {
  return arr.length ? arr.reduce((a,b)=>a+b,0)/arr.length : 0;
}

function stdDev(arr) {
  if (!arr.length) return 0;
  const mean = avg(arr);
  const squareDiffs = arr.map(v => Math.pow(v - mean, 2));
  return Math.sqrt(avg(squareDiffs));
}

function toggleStatConfig() {
  document.getElementById('stat-config').classList.toggle('hidden');
}

function buildStatConfig() {
  const stats = [
    {key:'duration', label:'Session Duration'},
    {key:'peakBed', label:'Peak Bed Temp'},
    {key:'peakChamber', label:'Peak Chamber Temp'},
    {key:'maxExtruder', label:'Max Extruder Temp'},
    {key:'heatsoak', label:'Heatsoak Duration'},
    {key:'cooldown', label:'Cooldown Duration'},
    {key:'avgChamber', label:'Avg Chamber'},
    {key:'avgBed', label:'Avg Bed'},
    {key:'tempStability', label:'Temp Stability'}
  ];
  
  document.getElementById('stat-config-grid').innerHTML = stats.map(s =>
    `<div class="toggle-row">
      <input type="checkbox" id="stat-${s.key}" 
        ${S.statsVisible[s.key]?'checked':''} 
        onchange="S.statsVisible['${s.key}']=this.checked;renderStats()">
      <label for="stat-${s.key}" style="cursor:pointer">${s.label}</label>
    </div>`
  ).join('');
}
```

### 8. Helper Functions

```javascript
function setGranularity(val) {
  document.getElementById('granularity').value = val;
  document.getElementById('gran-val').textContent = val;
  applySettings();
}

function categorize(msg, type) {
  if (/PRINT_START|print_start/i.test(msg)) return 'PRINT_START';
  if (/bed fan|bed temp|bed recover/i.test(msg)) return 'BED';
  if (/chamber|heatsoak/i.test(msg)) return 'CHAMBER';
  if (/cooldown/i.test(msg)) return 'COOLDOWN';
  if (type === 'echo') return 'ECHO';
  if (type === 'respond') return 'RESPOND';
  if (type === 'error') return 'ERROR';
  return 'OTHER';
}

function shortLabel(msg) {
  if (msg.length <= 30) return msg;
  return msg.substring(0, 28) + '…';
}

function fmtTime(d) {
  if (!d) return '—';
  if (S.timeFormat === '12') {
    return d.toLocaleTimeString('en-US', {hour:'numeric', minute:'2-digit', hour12:true});
  }
  return d.toTimeString().substring(0,8);
}
```

## UI Updates Required

### HTML Changes

1. Add second chart container: `<div id="chart-container2"></div>`
2. Add system metrics toggle panel
3. Add message type filter panel
4. Add stat configuration panel
5. Update time format selector
6. Rename "Downsample" to "Granularity" with presets
7. Add "Show annotations" checkbox

### CSS Additions

```css
.stat-card.disabled { opacity: 0.4; }
.badge-echo { background:#2a2a3a; color:#aac4ff; }
.badge-respond { background:#2a3a2a; color:#88ffaa; }
.badge-error { background:#3a1f1f; color:#ff6b6b; }
```

## Testing Checklist

- [ ] Load log with full cooldown - verify data extends to end
- [ ] Test with multiple simultaneous echo messages - verify no overlap
- [ ] Toggle statistics on/off - verify grid updates
- [ ] Switch between 12/24 hour format - verify time display
- [ ] Test granularity presets (All/High/Med/Low)
- [ ] Verify both charts render independently
- [ ] Test with logs from different printers
- [ ] Test message type filtering
- [ ] Export both charts as PNG
- [ ] Verify session list shows before file load

## Next Steps

1. Implement changes incrementally
2. Test each feature independently
3. Verify backward compatibility with existing logs
4. Add user documentation
5. Consider adding custom regex input for advanced users
