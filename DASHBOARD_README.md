# 🏗️ Innovation Architecture Generator - Dashboard

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Launch the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

### 3. Run the Pipeline

**Option A: From the Dashboard**
- Click the "▶️ Start Pipeline" button in the sidebar
- Watch real-time progress as stages complete

**Option B: From Terminal** (recommended for first run)
- Open a separate terminal
- Run: `python main.py`
- The dashboard will automatically pick up progress updates

## Dashboard Features

### 📈 Pipeline Progress Tab
- **Overall Metrics**: Stages completed, proposals generated, elapsed time, status
- **Stage Progress**: Real-time progress bars for each of the 10 pipeline stages
- **Status Indicators**:
  - 🔵 Pending
  - 🟡 Running
  - 🟢 Completed
  - 🔴 Error
  - ⚪ Skipped

### 📋 Proposals Tab
- **Interactive Cards**: View all generated proposals
- **Filtering**: Filter by source (streaming, event_sourcing, etc.)
- **Search**: Search proposals by name
- **Detailed View**: Expand to see thesis, components, innovations, scores

### 📊 Analytics Tab
- **Source Distribution**: Pie chart showing proposals by paradigm
- **Score Distribution**: Box plots of proposal scores
- **Timeline**: Gantt chart of pipeline execution timeline

### 🔧 Debug Tab
- **Progress File Info**: Path and status of progress JSON
- **Session State**: Current dashboard state
- **Raw Data**: Full progress JSON for debugging

## Dashboard Controls

### Sidebar Controls
- **▶️ Start Pipeline**: Launch the pipeline in background
- **🔄 Refresh**: Manually refresh the dashboard
- **🗑️ Clear Progress**: Reset all progress data
- **Auto-refresh**: Enable automatic updates (recommended)
- **Refresh Interval**: Set update frequency (1-10 seconds)
- **Show Detailed Logs**: Display detailed stage information

## How It Works

1. **Progress Tracking**: The pipeline emits progress updates to `outputs/progress.json`
2. **Real-time Updates**: Dashboard reads this file and auto-refreshes
3. **No API Needed**: Simple file-based communication between pipeline and dashboard

## Tips for Demo

1. **Prepare Clean State**:
   ```bash
   # Clear previous runs
   rm -rf outputs/
   ```

2. **Launch Dashboard First**:
   ```bash
   streamlit run dashboard.py
   ```

3. **Start Pipeline in Separate Terminal**:
   ```bash
   python main.py
   ```

4. **Watch the Magic** ✨:
   - Stages light up as they run
   - Proposals appear in real-time
   - Charts update automatically

## Customization

### Change Refresh Rate
Adjust in sidebar: "Refresh interval" slider

### Modify Colors/Styling
Edit the `st.markdown()` CSS in `dashboard.py` (lines 20-50)

### Add More Visualizations
Add new charts in the Analytics tab using Plotly:
```python
import plotly.express as px
fig = px.bar(data, x='metric', y='value')
st.plotly_chart(fig)
```

## Troubleshooting

**Dashboard not updating?**
- Check if `outputs/progress.json` exists
- Click "🔄 Refresh" button
- Enable "Auto-refresh" in sidebar

**Pipeline not starting from dashboard?**
- Use Option B (run from terminal) for more reliable execution
- Check terminal for error messages

**Port already in use?**
```bash
streamlit run dashboard.py --server.port 8502
```

## Screenshots

The dashboard includes:
- Beautiful gradient headers
- Color-coded status indicators
- Interactive charts and graphs
- Expandable proposal cards
- Real-time progress bars

Enjoy your demo! 🚀
