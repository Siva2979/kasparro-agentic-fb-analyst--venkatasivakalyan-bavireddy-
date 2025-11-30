import pandas as pd
import numpy as np
import json
import argparse
import sys
from datetime import timedelta, datetime
from typing import List, Dict, Any

# --- Configuration & Mock LLM ---
class Config:
    DATA_PATH = "synthetic_fb_ads_undergarments.csv"
    ROAS_THRESHOLD = 0.05
    CONFIDENCE_THRESHOLD = 0.8

class MockLLM:
    """Simulates LLM behavior for the assignment without needing API keys."""
    def generate_creative(self, bad_copy: str, inspiration: str) -> str:
        # Simple template-based mixing to simulate "rewriting"
        prefix = inspiration.split("—")[0].strip() if "—" in inspiration else inspiration[:20]
        suffix = " - Limited Time Offer."
        return f"{prefix} — {bad_copy.split('—')[-1].strip()} {suffix}"

# --- Agents ---

class DataAgent:
    def __init__(self, path: str):
        self.path = path
        self.df = None

    def load_and_clean(self):
        try:
            self.df = pd.read_csv(self.path)
            self.df['date'] = pd.to_datetime(self.df['date'])
            # Fill common metric gaps
            self.df.fillna({'spend': 0, 'clicks': 0, 'revenue': 0, 'purchases': 0}, inplace=True)
            return "Data loaded successfully."
        except Exception as e:
            return f"Error loading data: {str(e)}"

    def get_aggregated_stats(self, start_date=None, end_date=None):
        if self.df is None: self.load_and_clean()

        mask = pd.Series([True] * len(self.df))
        if start_date and end_date:
            mask = (self.df['date'] >= start_date) & (self.df['date'] <= end_date)

        filtered = self.df[mask]

        spend = filtered['spend'].sum()
        revenue = filtered['revenue'].sum()
        impressions = filtered['impressions'].sum()
        clicks = filtered['clicks'].sum()
        purchases = filtered['purchases'].sum()

        return {
            "spend": spend,
            "revenue": revenue,
            "roas": revenue / spend if spend > 0 else 0,
            "ctr": clicks / impressions if impressions > 0 else 0,
            "cpc": spend / clicks if clicks > 0 else 0,
            "cpm": (spend / impressions) * 1000 if impressions > 0 else 0,
            "aov": revenue / purchases if purchases > 0 else 0
        }

    def get_bad_creatives(self, ctr_threshold=0.012):
        """Identify creatives with low CTR but significant spend."""
        perf = self.df.groupby('creative_message')[['spend', 'clicks', 'impressions']].sum().reset_index()
        perf['ctr'] = perf['clicks'] / perf['impressions']
        return perf[(perf['ctr'] < ctr_threshold) & (perf['spend'] > 1000)].sort_values('spend', ascending=False)

    def get_top_creatives(self, n=5):
        perf = self.df.groupby('creative_message')['roas'].mean().sort_values(ascending=False)
        return perf.head(n).index.tolist()

class InsightAgent:
    def analyze_drop(self, current_stats: Dict, prev_stats: Dict) -> Dict:
        """Heuristic analysis of why ROAS dropped."""
        roas_diff = (current_stats['roas'] - prev_stats['roas']) / prev_stats['roas']

        drivers = []
        if current_stats['cpm'] > prev_stats['cpm'] * 1.05:
            drivers.append("CPM Increase (Competition/Fatigue)")
        if current_stats['ctr'] < prev_stats['ctr'] * 0.95:
            drivers.append("CTR Drop (Creative Fatigue)")
        if current_stats['aov'] < prev_stats['aov'] * 0.95:
            drivers.append("AOV Drop (Lower value bundles sold)")
        if current_stats['cpc'] > prev_stats['cpc'] * 1.05:
            drivers.append("CPC Spike")

        return {
            "is_drop": roas_diff < -0.05,
            "pct_change": roas_diff,
            "primary_driver": drivers[0] if drivers else "Unknown/Multi-factor",
            "all_drivers": drivers
        }

class CreativeGenerator:
    def __init__(self):
        self.llm = MockLLM()

    def generate_fixes(self, bad_creatives, top_examples):
        recommendations = []
        for _, row in bad_creatives.head(3).iterrows():
            bad_copy = row['creative_message']
            # Pick a random "winner" to emulate style
            inspiration = np.random.choice(top_examples)

            new_copy = self.llm.generate_creative(bad_copy, inspiration)

            recommendations.append({
                "original": bad_copy,
                "inspiration_source": inspiration,
                "suggested_variation": new_copy,
                "rationale": "Applied high-converting hook from top performer to low-CTR ad."
            })
        return recommendations

class PlannerAgent:
    def __init__(self):
        self.data_agent = DataAgent(Config.DATA_PATH)
        self.insight_agent = InsightAgent()
        self.creative_agent = CreativeGenerator()

    def run(self, query: str):
        print(f" Planner: Received query -> '{query}'")

        # Step 1: Data Loading
        print(" Planner: Instructing Data Agent to load data...")
        self.data_agent.load_and_clean()

        # Step 2: Time Analysis (Last 14 days vs Previous 14 days)
        max_date = self.data_agent.df['date'].max()
        mid_date = max_date - timedelta(days=14)
        start_date = mid_date - timedelta(days=14)

        curr_stats = self.data_agent.get_aggregated_stats(mid_date, max_date)
        prev_stats = self.data_agent.get_aggregated_stats(start_date, mid_date)

        # Step 3: Insight Generation
        print("Planner: Analyzing patterns for ROAS drop...")
        analysis = self.insight_agent.analyze_drop(curr_stats, prev_stats)

        # Step 4: Creative Action
        creatives = []
        if analysis['is_drop'] or "CTR" in str(analysis['all_drivers']):
            print(" Planner: Low performance detected. Generating creative fixes...")
            bad_ads = self.data_agent.get_bad_creatives()
            top_ads = self.data_agent.get_top_creatives()
            creatives = self.creative_agent.generate_fixes(bad_ads, top_ads)

        # Step 5: Report
        report = {
            "period_analyzed": f"{mid_date.date()} to {max_date.date()}",
            "roas_change": f"{analysis['pct_change']*100:.2f}%",
            "drivers": analysis['all_drivers'],
            "metrics": {
                "current_roas": round(curr_stats['roas'], 2),
                "previous_roas": round(prev_stats['roas'], 2),
                "current_ctr": round(curr_stats['ctr'], 4),
                "previous_ctr": round(prev_stats['ctr'], 4)
            },
            "creative_recommendations": creatives
        }

        return report

# --- CLI Entrypoint ---
if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Analyze ROAS drop"
    planner = PlannerAgent()
    result = planner.run(query)

    # Save outputs
    with open('reports/insights.json', 'w') as f:
        json.dump(result, f, indent=2)

    with open('reports/creatives.json', 'w') as f:
        json.dump(result['creative_recommendations'], f, indent=2)

    print("\n Analysis Complete. Results saved to reports/")
    print(json.dumps(result, indent=2))
