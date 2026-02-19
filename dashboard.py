"""
Streamlit Dashboard for Innovation Architecture Generator
Real-time visualization of the multi-agent pipeline
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import json
import time
import asyncio
from datetime import datetime
import sys

# Page config
st.set_page_config(
    page_title="Innovation Architecture Generator",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .stage-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    .proposal-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 2px solid #e9ecef;
        background-color: white;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    .proposal-card h3 {
        color: #000000 !important;
        margin-bottom: 0.5rem;
    }
    .proposal-card h4 {
        color: #666666 !important;
        font-size: 1.1rem;
        font-weight: normal;
        margin-top: 0;
    }
    .proposal-card p, .proposal-card strong {
        color: #333333 !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🏗️ Innovation Architecture Generator</h1>', unsafe_allow_html=True)
st.markdown("**Multi-Agent Pipeline for Generating Innovative Data Architecture Proposals**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    # Pipeline control
    st.subheader("Pipeline Control")

    if st.button("▶️ Start Pipeline", type="primary"):
        st.session_state.pipeline_running = True
        st.session_state.start_time = datetime.now()
        # Start pipeline in background
        import subprocess
        subprocess.Popen([sys.executable, "main.py"])
        st.rerun()

    if st.button("🔄 Refresh"):
        st.rerun()

    if st.button("🗑️ Clear Progress"):
        progress_file = Path("outputs/progress.json")
        if progress_file.exists():
            progress_file.unlink()
        st.session_state.clear()
        st.rerun()

    st.markdown("---")

    # Settings
    st.subheader("Visualization Settings")
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    refresh_interval = st.slider("Refresh interval (seconds)", 1, 10, 3)
    show_details = st.checkbox("Show detailed logs", value=False)

    st.markdown("---")
    st.caption("💡 **Tip:** The dashboard updates automatically as the pipeline runs")

# Initialize session state
if 'pipeline_running' not in st.session_state:
    st.session_state.pipeline_running = False

# Load progress data
progress_file = Path("outputs/progress.json")
progress_data = {}
if progress_file.exists():
    with open(progress_file, 'r') as f:
        progress_data = json.load(f)

# Pipeline stages
STAGES = [
    ("0a", "Intent Agent", "🎯"),
    ("0b", "Prompt Enhancement", "✨"),
    ("1", "Paradigm Agents", "🧠"),
    ("2", "Mutation Engine", "🧬"),
    ("2.5", "Diversity Archive", "🌈"),
    ("3", "Self-Refinement", "💎"),
    ("4", "Physics Critic", "⚖️"),
    ("4.5", "Structured Debate", "⚔️"),
    ("4.7", "Domain Critics", "🔍"),
    ("5", "Portfolio Assembly", "📊"),
]

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["📈 Pipeline Progress", "📋 Proposals", "📊 Analytics", "🔧 Debug"])

with tab1:
    # Overall progress
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_stages = len(STAGES)
        completed_stages = sum(1 for stage_id, _, _ in STAGES if progress_data.get(f"stage_{stage_id}", {}).get("status") == "completed")
        st.markdown(f"""
        <div class="metric-card">
            <h3>{completed_stages}/{total_stages}</h3>
            <p>Stages Completed</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Show final portfolio count if available, otherwise stage 5 outputs
        portfolio_count = progress_data.get("stage_5", {}).get("outputs_count", 0)
        if portfolio_count == 0:
            portfolio_count = progress_data.get("total_proposals", 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{portfolio_count}</h3>
            <p>Final Proposals</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        elapsed_time = "Not started"
        if progress_data.get("start_time"):
            start = datetime.fromisoformat(progress_data["start_time"])
            if progress_data.get("end_time"):
                end = datetime.fromisoformat(progress_data["end_time"])
            else:
                end = datetime.now()
            elapsed = end - start
            elapsed_time = f"{int(elapsed.total_seconds())}s"

        st.markdown(f"""
        <div class="metric-card">
            <h3>{elapsed_time}</h3>
            <p>Elapsed Time</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        status = progress_data.get("status", "idle")
        status_emoji = {"idle": "⏸️", "running": "▶️", "completed": "✅", "error": "❌"}.get(status, "❓")
        st.markdown(f"""
        <div class="metric-card">
            <h3>{status_emoji}</h3>
            <p>{status.title()}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Stage progress
    st.subheader("📍 Stage Progress")

    for stage_id, stage_name, emoji in STAGES:
        stage_key = f"stage_{stage_id}"
        stage_data = progress_data.get(stage_key, {})
        status = stage_data.get("status", "pending")

        # Status colors
        status_colors = {
            "pending": "🔵",
            "running": "🟡",
            "completed": "🟢",
            "error": "🔴",
            "skipped": "⚪"
        }

        status_icon = status_colors.get(status, "⚫")

        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**{emoji} Stage {stage_id}: {stage_name}** {status_icon}")

                if status == "running":
                    progress = stage_data.get("progress", 0)
                    st.progress(progress / 100 if progress > 0 else 0)
                elif status == "completed":
                    st.progress(1.0)
                    if stage_data.get("duration"):
                        st.caption(f"✓ Completed in {stage_data['duration']:.1f}s")
                elif status == "error":
                    st.error(f"Error: {stage_data.get('error', 'Unknown error')}")

            with col2:
                if stage_data.get("outputs_count"):
                    st.metric("Outputs", stage_data["outputs_count"])

        if show_details and stage_data.get("details"):
            with st.expander("Show details"):
                st.json(stage_data["details"])

with tab2:
    st.subheader("📋 Final Portfolio Proposals")

    # Load portfolio.json for final ranked proposals
    portfolio_file = Path("outputs/portfolio.json")

    if not portfolio_file.exists():
        st.info("Portfolio not generated yet. Complete the pipeline to see ranked proposals.")
    else:
        try:
            with open(portfolio_file, 'r', encoding='utf-8') as f:
                portfolio = json.load(f)

            portfolio_proposals = portfolio.get("proposals", [])

            if not portfolio_proposals:
                st.warning("No proposals in portfolio")
            else:
                # Extract proposal data with tier and scores
                proposals_data = []
                for p in portfolio_proposals:
                    nested = p.get("proposal", {}).get("proposal", {})
                    proposals_data.append({
                        "architecture_name": nested.get("architecture_name"),
                        "core_thesis": nested.get("core_thesis"),
                        "components": nested.get("components", []),
                        "key_innovations": nested.get("key_innovations", []),
                        "paradigm_source": nested.get("paradigm_source"),
                        "tier": p.get("tier", "unknown"),
                        "innovation_score": p.get("innovation_score", 0),
                        "feasibility_score": p.get("feasibility_score", 0),
                        "business_alignment_score": p.get("business_alignment_score", 0),
                        "migration_complexity_score": p.get("migration_complexity_score", 0),
                        "composite_score": p.get("composite_score", 0),
                        "summary": p.get("one_line_summary", "")
                    })

                # Fixed tier categories (always available)
                all_tiers = ["Conservative", "Moderate", "Radical"]

                # Filters row
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    tier_options = ["All Tiers"] + all_tiers
                    tier_filter = st.selectbox(
                        "Filter by Tier",
                        tier_options,
                        index=0
                    )
                with col2:
                    top_n = st.selectbox(
                        "Show",
                        ["All proposals", "Top 3 per tier", "Top 3 overall"],
                        index=0
                    )

                # Filter by tier
                if tier_filter != "All Tiers":
                    filtered = [p for p in proposals_data if tier_filter.lower() in p["tier"].lower()]
                else:
                    filtered = proposals_data

                # Sort by composite score (highest first)
                filtered = sorted(filtered, key=lambda x: x["composite_score"], reverse=True)

                # Apply top-N logic
                if top_n == "Top 3 overall":
                    filtered = filtered[:3]
                elif top_n == "Top 3 per tier":
                    tier_buckets = {}
                    for p in filtered:
                        t = p["tier"].replace("_", " ").title().split()[0]
                        tier_buckets.setdefault(t, []).append(p)
                    top_filtered = []
                    for t in all_tiers:
                        top_filtered.extend(tier_buckets.get(t, [])[:3])
                    # Re-sort combined list
                    filtered = sorted(top_filtered, key=lambda x: x["composite_score"], reverse=True)

                with col3:
                    if tier_filter == "All Tiers" and top_n == "All proposals":
                        st.metric("Total Proposals", len(filtered))
                    else:
                        st.metric("Showing", f"{len(filtered)} / {len(proposals_data)}")

                # Display proposals
                for i, proposal in enumerate(filtered):
                    arch_name = proposal["architecture_name"]
                    tier = proposal["tier"].replace("_", " ").title()
                    tier_emoji = {"Conservative": "🛡️", "Moderate": "⚖️", "Radical": "🚀"}.get(tier.split()[0], "📋")
                    tier_label = f"{tier_emoji} {tier.upper()}"

                    with st.container():
                        st.markdown(f"""
                        <div class="proposal-card">
                            <h3>{tier_label}</h3>
                            <h4 style="color: #666; margin-top: 0.5rem;">{arch_name}</h4>
                            <p><strong>Composite Score:</strong> {proposal['composite_score']:.2f}/10</p>
                            <p style="font-style: italic; color: #555;">{proposal['summary']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        with st.expander("View Details"):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.markdown("**Core Thesis:**")
                                st.write(proposal['core_thesis'])

                                st.markdown("**Key Innovations:**")
                                for innovation in proposal['key_innovations']:
                                    st.markdown(f"- {innovation}")

                            with col2:
                                st.markdown("**Components:**")
                                for comp in proposal['components']:
                                    st.markdown(f"- **{comp.get('name')}**: {comp.get('role')}")

                                st.markdown("**Scores:**")
                                scores = {
                                    "Innovation": proposal['innovation_score'],
                                    "Feasibility": proposal['feasibility_score'],
                                    "Business": proposal['business_alignment_score'],
                                    "Migration": proposal['migration_complexity_score']
                                }
                                fig = go.Figure(data=[
                                    go.Bar(
                                        x=list(scores.keys()),
                                        y=list(scores.values()),
                                        marker_color='#667eea',
                                        text=[f"{v:.1f}" for v in scores.values()],
                                        textposition='outside'
                                    )
                                ])
                                fig.update_layout(
                                    height=250,
                                    margin=dict(l=0, r=0, t=20, b=0),
                                    yaxis=dict(range=[0, 10])
                                )
                                st.plotly_chart(fig, width="stretch")

        except Exception as e:
            st.error(f"Error loading portfolio: {e}")
            import traceback
            st.code(traceback.format_exc())

with tab3:
    st.subheader("📊 Pipeline Analytics")

    proposals = progress_data.get("proposals", [])

    if proposals:
        # Score Distribution
        st.markdown("**Score Distribution**")
        if any(p.get('scores') for p in proposals):
            scores_data = []
            for p in proposals:
                if p.get('scores'):
                    for metric, value in p['scores'].items():
                        scores_data.append({
                            'Metric': metric,
                            'Score': value,
                            'Proposal': p.get('architecture_name', 'Unknown')
                        })

            if scores_data:
                import pandas as pd
                df = pd.DataFrame(scores_data)
                fig = px.box(df, x='Metric', y='Score', color='Metric')
                st.plotly_chart(fig, width="stretch")

        # Radar Chart — Portfolio Proposal Comparison
        st.markdown("**Radar Chart — Proposal Comparison**")
        portfolio_file_analytics = Path("outputs/portfolio.json")
        if portfolio_file_analytics.exists():
            try:
                with open(portfolio_file_analytics, 'r', encoding='utf-8') as f:
                    portfolio_analytics = json.load(f)
                radar_proposals = portfolio_analytics.get("proposals", [])
                if radar_proposals:
                    dimensions = ["innovation_score", "feasibility_score",
                                  "business_alignment_score", "migration_complexity_score"]
                    dim_labels = ["Innovation", "Feasibility", "Business Alignment", "Migration Complexity"]
                    colors = ["#667eea", "#764ba2", "#f093fb", "#4facfe", "#00f2fe"]

                    fig_radar = go.Figure()
                    for idx, rp in enumerate(radar_proposals):
                        name = rp.get("proposal", {}).get("proposal", {}).get("architecture_name", f"Proposal {idx+1}")
                        # Truncate long names for the legend
                        short_name = name if len(name) <= 40 else name[:37] + "..."
                        values = [rp.get(d, 0) for d in dimensions]
                        values.append(values[0])  # close the polygon

                        fig_radar.add_trace(go.Scatterpolar(
                            r=values,
                            theta=dim_labels + [dim_labels[0]],
                            fill='toself',
                            name=short_name,
                            line=dict(color=colors[idx % len(colors)]),
                            opacity=0.6
                        ))

                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                        height=450,
                        margin=dict(l=60, r=60, t=40, b=40),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig_radar, width="stretch")
                else:
                    st.info("No proposals in portfolio for radar chart.")
            except Exception:
                st.warning("Could not load portfolio data for radar chart.")
        else:
            st.info("Portfolio not generated yet — radar chart will appear after the pipeline completes.")

        st.markdown("---")

        # Proposals Funnel
        st.markdown("**Proposals Funnel — Pipeline Narrowing**")
        funnel_stages = []
        funnel_counts = []

        # Stage 1: Paradigm Agents — original proposals
        stage_1 = progress_data.get("stage_1", {})
        if stage_1.get("outputs_count"):
            funnel_stages.append("Paradigm Agents")
            funnel_counts.append(stage_1["outputs_count"])

        # Stage 2: Mutation Engine — originals + mutations
        stage_2 = progress_data.get("stage_2", {})
        if stage_2.get("outputs_count"):
            originals = funnel_counts[-1] if funnel_counts else 0
            funnel_stages.append("After Mutations")
            funnel_counts.append(originals + stage_2["outputs_count"])

        # Stage 2.5: Diversity Archive — top-k selection
        stage_25 = progress_data.get("stage_2.5", {})
        if stage_25.get("outputs_count"):
            funnel_stages.append("Diversity Archive (top-k)")
            funnel_counts.append(stage_25["outputs_count"])

        # Stage 5: Portfolio Assembly — final scored
        stage_5 = progress_data.get("stage_5", {})
        if stage_5.get("outputs_count"):
            funnel_stages.append("Final Portfolio")
            funnel_counts.append(stage_5["outputs_count"])

        if funnel_stages:
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_stages,
                x=funnel_counts,
                textinfo="value+percent initial",
                marker=dict(color=["#667eea", "#764ba2", "#f093fb", "#4facfe"][:len(funnel_stages)]),
                connector=dict(line=dict(color="#aaa", width=1))
            ))
            fig_funnel.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_funnel, width="stretch")
        else:
            st.info("Funnel data will appear after the pipeline runs (requires stage output counts).")

        st.markdown("---")

        # Timeline
        st.markdown("**Pipeline Timeline**")
        timeline_data = []
        for stage_id, stage_name, emoji in STAGES:
            stage_data = progress_data.get(f"stage_{stage_id}", {})
            if stage_data.get("start_time"):
                timeline_data.append({
                    'Stage': f"{emoji} {stage_name}",
                    'Start': stage_data.get('start_time'),
                    'End': stage_data.get('end_time', datetime.now().isoformat()),
                    'Duration': stage_data.get('duration', 0)
                })

        if timeline_data:
            import pandas as pd
            df = pd.DataFrame(timeline_data)
            df['Start'] = pd.to_datetime(df['Start'])
            df['End'] = pd.to_datetime(df['End'])

            fig = px.timeline(df, x_start='Start', x_end='End', y='Stage', color='Duration')
            fig.update_layout(height=400)
            st.plotly_chart(fig, width="stretch")
    else:
        st.info("Run the pipeline to see analytics")

with tab4:
    st.subheader("🔧 Debug Information")

    # System info
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Progress File**")
        st.code(str(progress_file))
        st.markdown(f"**Exists:** {progress_file.exists()}")
        if progress_file.exists():
            st.markdown(f"**Size:** {progress_file.stat().st_size} bytes")

    with col2:
        st.markdown("**Session State**")
        st.json(dict(st.session_state))

    st.markdown("---")

    # All Proposals (from progress.json)
    st.markdown("### All Proposals (Generated During Pipeline)")
    all_proposals = progress_data.get("proposals", [])

    if all_proposals:
        st.info(f"Total proposals generated: {len(all_proposals)}")

        # Group by source
        by_source = {}
        for p in all_proposals:
            source = p.get("paradigm_source", "unknown")
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(p)

        for source, props in sorted(by_source.items()):
            with st.expander(f"{source} ({len(props)} proposals)"):
                for p in props:
                    st.markdown(f"**{p.get('architecture_name', 'Unnamed')}**")
                    st.write(f"Core Thesis: {p.get('core_thesis', 'N/A')[:150]}...")
                    if p.get('scores'):
                        st.write(f"Scores: {p['scores']}")
                    st.markdown("---")
    else:
        st.warning("No proposals found in progress data")

    st.markdown("---")

    # Stage Details
    st.markdown("### Stage Execution Details")

    for stage_id, stage_name, emoji in STAGES:
        stage_key = f"stage_{stage_id}"
        stage_data = progress_data.get(stage_key, {})

        if stage_data:
            status = stage_data.get("status", "unknown")
            status_emoji = {"pending": "🔵", "running": "🟡", "completed": "🟢", "error": "🔴", "skipped": "⚪"}.get(status, "⚫")

            with st.expander(f"{emoji} Stage {stage_id}: {stage_name} {status_emoji}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Status", status.upper())
                    if stage_data.get("outputs_count"):
                        st.metric("Outputs", stage_data["outputs_count"])

                with col2:
                    if stage_data.get("duration"):
                        st.metric("Duration", f"{stage_data['duration']:.1f}s")
                    if stage_data.get("progress"):
                        st.metric("Progress", f"{stage_data['progress']}%")

                with col3:
                    if stage_data.get("start_time"):
                        st.write(f"**Start:** {stage_data['start_time'].split('T')[1][:8]}")
                    if stage_data.get("end_time"):
                        st.write(f"**End:** {stage_data['end_time'].split('T')[1][:8]}")

                if stage_data.get("error"):
                    st.error(f"Error: {stage_data['error']}")

                if stage_data.get("details"):
                    st.markdown("**Details:**")
                    st.json(stage_data["details"])

    st.markdown("---")

    # Raw JSON (collapsed by default)
    with st.expander("📄 Raw Progress Data (JSON)"):
        if progress_data:
            st.json(progress_data)
        else:
            st.info("No progress data available")

# Auto-refresh
if auto_refresh and st.session_state.get('pipeline_running'):
    time.sleep(refresh_interval)
    st.rerun()
