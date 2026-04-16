import streamlit as st
import google.generativeai as genai
import os
import json
import pandas as pd
import plotly.express as px

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & SESSION STATE
# -------------------------------------------------------------
st.set_page_config(
    page_title="Ultimate AI Product Review Analyzer", 
    page_icon="🚀", 
    layout="wide"
)

if "target_pct" not in st.session_state:
    st.session_state.target_pct = 80
if "chart_type" not in st.session_state:
    st.session_state.chart_type = "Donut Chart"
if "selected_filters" not in st.session_state:
    st.session_state.selected_filters = ["Positive", "Negative", "Mixed"]

# -------------------------------------------------------------
# 2. ANALYSIS FUNCTION
# -------------------------------------------------------------
@st.cache_data(show_spinner=False)
def analyze_reviews(text: str, target_percentage: int) -> dict:
    """Sends reviews to the Gemini API and extracts interactive insights."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
    You are an expert business analyst. Analyze these customer reviews.
    The business has a goal of achieving {target_percentage}% positive reviews.
    
    Respond STRICTLY in JSON with the exact structure below, nothing else:
    {{
      "sentiment": "Positive" | "Negative" | "Mixed",
      "sentiment_counts": {{
        "Positive": <int>,
        "Negative": <int>,
        "Mixed": <int>
      }},
      "problems": [
        {{"issue": "Brief text", "priority": "High" | "Medium" | "Low", "reason": "Short reason for this priority"}}
      ],
      "positives": [
        {{"category": "Main Category (Choose 1 of 5-7 generalized themes)", "aspect": "Specific positive note"}}
      ],
      "recommendations": [
        {{"recommendation": "Actionable business recommendation", "helps_target": true | false}}
      ],
      "analyzed_reviews": [
        {{"text": "Short excerpt", "sentiment": "Positive" | "Negative" | "Mixed", "category": "Theme Category"}}
      ]
    }}

    Reviews to analyze:
    {text}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.2 
            )
        )
        return json.loads(response.text)
    
    except Exception as e:
        raise RuntimeError(f"Failed to communicate with Gemini API: {str(e)}")

# -------------------------------------------------------------
# 3. HELPER STYLING FUNCTIONS
# -------------------------------------------------------------
def color_priority(val):
    val_str = str(val).lower()
    if 'high' in val_str: return 'background-color: #FFCCCC; color: #990000;'
    elif 'medium' in val_str: return 'background-color: #FFE6CC; color: #CC6600;'
    elif 'low' in val_str: return 'background-color: #E6FFCC; color: #336600;'
    return ''

def color_sentiment(val):
    val_str = str(val).lower()
    if 'positive' in val_str: return 'background-color: #D4EDDA; color: #155724;'
    elif 'negative' in val_str: return 'background-color: #F8D7DA; color: #721C24;'
    elif 'mixed' in val_str: return 'background-color: #E2E3E5; color: #383D41;'
    return ''

# -------------------------------------------------------------
# 4. USER INTERFACE & SIDEBAR SETTINGS
# -------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Preferences & Filters")
    st.caption("Customize your experience and save layout defaults.")
    
    input_target = st.slider(
        "🎯 Target Positive Reviews (%)", 
        0, 100, st.session_state.target_pct, 5,
        help="Adjust your target goal. Recommendations will rebuild dynamically."
    )
    
    input_chart = st.selectbox(
        "📊 Visualization Style", 
        ["Donut Chart", "Pie Chart", "Bar Chart"],
        index=["Donut Chart", "Pie Chart", "Bar Chart"].index(st.session_state.chart_type),
        help="Pick the chart type you find most visually pleasing."
    )
    
    st.write("---")
    if st.button("💾 Save My Dashboard Preferences", use_container_width=True, help="Locks in Target% and Chart types!"):
        st.session_state.target_pct = input_target
        st.session_state.chart_type = input_chart
        st.success("Preferences Saved successfully!")

# Ensure live variables pull from session cache accurately
active_target = st.session_state.target_pct
active_chart = st.session_state.chart_type

st.title("🚀 Ultimate AI Product Review Analyzer")
st.markdown("Unlock deep insights with goal-driven AI recommendations, gamified tracking, and adaptive visualizations.")
st.divider()

col_input, col_results = st.columns([1, 2], gap="large")

with col_input:
    with st.container(border=True):
        st.subheader("📝 Input Data", help="Provide your raw customer comments manually or by text file.")
        uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
        text_area = st.text_area("Or paste reviews here", height=200)

        input_text = ""
        if uploaded_file is not None:
            input_text = uploaded_file.getvalue().decode("utf-8")
        elif text_area.strip():
            input_text = text_area.strip()

        analyze_btn = st.button("🔍 Run Full AI Analysis", type="primary", use_container_width=True)

if analyze_btn:
    if not input_text:
        with col_input:
            st.warning("⚠️ Please provide reviews before running analysis.")
    else:
        with col_results:
            with st.spinner("Processing advanced diagnostics via Gemini framework..."):
                try:
                    results = analyze_reviews(input_text, active_target)
                    st.success("✅ Results Generated Successfully!")
                    
                    tab_overview, tab_details, tab_recs = st.tabs([
                        "📊 Analytics Overview", 
                        "📋 Adaptive Tables & Filters", 
                        "💡 Focus Recommendations"
                    ])
                    
                    # --- TAB 1: OVERVIEW & GAMIFICATION ---
                    with tab_overview:
                        with st.container(border=True):
                            counts = results.get("sentiment_counts", {"Positive": 0, "Negative": 0, "Mixed": 0})
                            total = sum(counts.values())
                            pos_pct = (counts.get("Positive", 0) / total * 100) if total > 0 else 0
                            
                            st.subheader("🏁 Live Gamified Tracker", help="Tracks progress against your saved Target %.")
                            progress_val = min(pos_pct / 100.0, 1.0)
                            st.progress(progress_val)
                            
                            if pos_pct >= active_target and total > 0:
                                st.success(f"🏆 Goal Achieved! Phenomenal job hitting **{pos_pct:.1f}%**!")
                                st.balloons()
                            elif pos_pct >= active_target * 0.8 and total > 0:
                                st.info("🔥 Almost there! Keep pushing, you are very close to your goal.")
                            elif total > 0:
                                st.warning("💪 Room to grow. Consult the Actionable Recommendations tab for next steps!")
                            
                            st.write("---")
                            
                            sentiment = results.get("sentiment", "Mixed")
                            icon = "😊" if sentiment == "Positive" else "😡" if sentiment == "Negative" else "😐"
                            st.metric(
                                label="Current Review Sentiment Ratio", 
                                value=f"{pos_pct:.1f}%", 
                                delta=f"{pos_pct - active_target:.1f}% vs Target",
                                delta_color="normal",
                            )
                            
                            # Adaptive Plotly Logic 
                            df_counts = pd.DataFrame(list(counts.items()), columns=["Sentiment", "Count"])
                            color_map = {"Positive": "#2ECC71", "Negative": "#E74C3C", "Mixed": "#95A5A6"}
                            
                            if active_chart == "Bar Chart":
                                fig = px.bar(
                                    df_counts, x='Sentiment', y='Count', color='Sentiment',
                                    color_discrete_map=color_map, text_auto=True
                                )
                                fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), transition_duration=500)
                            else:
                                hole_size = 0.4 if active_chart == "Donut Chart" else 0
                                fig = px.pie(
                                    df_counts, values='Count', names='Sentiment', color='Sentiment',
                                    color_discrete_map=color_map, hover_data=['Count'], hole=hole_size
                                )
                                fig.update_traces(textposition='inside', textinfo='percent+label+value', pull=[0.05, 0, 0])
                                fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), transition_duration=500)
                            
                            st.plotly_chart(fig, use_container_width=True)

                    # --- TAB 2: DATA TABLES AND EXPORTS ---
                    with tab_details:
                        
                        # Top Problems Table
                        with st.container(border=True):
                            st.subheader("⚠️ High Priority Issues", help="AI-categorized urgent roadblocks for your customers. Severity defines the priority flag.")
                            problems = results.get("problems", [])
                            if problems:
                                df_prob = pd.DataFrame(problems)
                                def map_priority(p):
                                    if "High" in str(p): return "🔴 High"
                                    if "Medium" in str(p): return "🟠 Medium"
                                    return "🟡 Low"
                                df_prob['priority'] = df_prob['priority'].apply(map_priority)
                                df_prob.rename(columns={'issue': 'Reported Issue', 'priority': 'Priority Level', 'reason': 'Why?'}, inplace=True)
                                
                                try:
                                    styled_prob = df_prob.style.map(color_priority, subset=['Priority Level'])
                                except AttributeError:
                                    styled_prob = df_prob.style.applymap(color_priority, subset=['Priority Level'])
                                    
                                st.dataframe(styled_prob, use_container_width=True, hide_index=True)
                            else:
                                st.success("No major problems found! 🎉")
                        
                        # Top Positives Table
                        with st.container(border=True):
                            st.subheader("🌟 Core Strengths", help="Positive highlights categorized into unified business themes.")
                            positives = results.get("positives", [])
                            if positives:
                                df_pos = pd.DataFrame(positives)
                                df_pos.rename(columns={'category': 'Global Theme', 'aspect': 'Direct Feedback'}, inplace=True)
                                st.dataframe(df_pos, use_container_width=True, hide_index=True)
                            else:
                                st.info("No explicit positive strengths detected.")
                                
                        # Review Filter Table
                        with st.container(border=True):
                            st.subheader("🔍 Customizable Data Grid", help="Utilize the selector to quickly segment data snippets. This configuration is purely interactive.")
                            reviews_data = results.get("analyzed_reviews", [])
                            if reviews_data:
                                df_rev = pd.DataFrame(reviews_data)
                                df_rev.rename(columns={'text': 'Review Excerpt', 'sentiment': 'Sentiment', 'category': 'Sub Category'}, inplace=True)
                                
                                # Filter Checkbox UI Hook
                                filter_sent = st.multiselect("Visible Dashboard Sentiments", options=df_rev['Sentiment'].unique(), default=st.session_state.selected_filters)
                                st.session_state.selected_filters = filter_sent # Memorize filters
                                
                                filtered_df = df_rev[df_rev['Sentiment'].isin(filter_sent)]
                                
                                try:
                                    styled_rev = filtered_df.style.map(color_sentiment, subset=['Sentiment'])
                                except AttributeError:
                                    styled_rev = filtered_df.style.applymap(color_sentiment, subset=['Sentiment'])
                                
                                st.dataframe(styled_rev, use_container_width=True, hide_index=True, height=250)

                    # --- TAB 3: RECOMMENDATIONS ---
                    with tab_recs:
                        with st.container(border=True):
                            st.subheader(f"💡 Targeted Game Plan", help="Specific directives tailored heavily to your Target Goal configurations.")
                            recs = results.get("recommendations", [])
                            if recs:
                                for i, r in enumerate(recs, 1):
                                    text = r.get("recommendation", "")
                                    is_target = r.get("helps_target", False)
                                    
                                    if is_target:
                                        target_color = "#2ECC71"
                                        st.markdown(f"**{i}.** :star2: {text} <br><span style='color:{target_color};'>*(Crucial tactic to achieve {active_target}% target)*</span>", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"**{i}.** {text}")
                            else:
                                st.info("Not enough exact feedback to generate reliable insights.")
                                
                except Exception as e:
                    st.error(f"❌ Core processing error. Details:\n\n{str(e)}")
