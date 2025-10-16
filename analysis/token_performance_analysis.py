"""
Token Performance Analysis Script

This script analyzes token filter effectiveness, price performance,
and legitimacy detection using data from Supabase time_series_data table.

Features:
- Filter transition analysis (PASS→FAIL, FAIL→PASS)
- ROI calculation for PASS vs FAIL tokens
- Legitimacy scoring (Real/Meme/Scam classification)
- Filter effectiveness metrics (precision/recall)
- Visualizations and exportable reports

Usage:
    python analysis/token_performance_analysis.py

Requirements:
    pip install pandas matplotlib seaborn sqlalchemy psycopg2-binary python-dotenv
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import SQLAlchemy for pandas compatibility
try:
    from sqlalchemy import create_engine
    HAS_SQLALCHEMY = True
except ImportError:
    print("⚠️  SQLAlchemy not installed. Install with: pip install sqlalchemy")
    HAS_SQLALCHEMY = False

load_dotenv()

# Set matplotlib style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class TokenAnalyzer:
    """Analyzes token performance and filter effectiveness"""

    def __init__(self):
        """Initialize database connection using SQLAlchemy"""
        if not HAS_SQLALCHEMY:
            raise ImportError("SQLAlchemy is required. Install with: pip install sqlalchemy psycopg2-binary")

        # Build PostgreSQL connection string
        host = os.getenv("SUPABASE_HOST")
        port = os.getenv("SUPABASE_PORT", "5432")
        user = os.getenv("SUPABASE_USERNAME")
        password = os.getenv("SUPABASE_PASSWORD")
        dbname = os.getenv("SUPABASE_DBNAME")

        # Create SQLAlchemy engine (pandas-compatible)
        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        self.engine = create_engine(connection_string)

        print("✅ Connected to Supabase database")

        # Create output directory
        self.output_dir = "analysis/output"
        os.makedirs(self.output_dir, exist_ok=True)

    def query_to_dataframe(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return results as pandas DataFrame"""
        return pd.read_sql_query(query, self.engine)

    def analyze_filter_transitions(self) -> Dict:
        """
        Analyze filter status transitions (PASS→FAIL and FAIL→PASS)

        Returns:
            Dict with transition statistics and DataFrames
        """
        print("\n" + "="*70)
        print("1. FILTER TRANSITION ANALYSIS")
        print("="*70)

        # PASS → FAIL transitions
        pass_to_fail_query = """
        WITH token_statuses AS (
            SELECT
                token_address,
                snapshot_at,
                filter_status,
                filter_fail_reasons,
                price_usd,
                liquidity_usd,
                LAG(filter_status) OVER (PARTITION BY token_address ORDER BY snapshot_at) as prev_status
            FROM time_series_data
            WHERE filter_status IS NOT NULL
        )
        SELECT
            token_address,
            snapshot_at as failed_at,
            filter_fail_reasons,
            EXTRACT(EPOCH FROM (snapshot_at - LAG(snapshot_at) OVER (PARTITION BY token_address ORDER BY snapshot_at))) / 3600 as hours_to_failure,
            price_usd,
            liquidity_usd
        FROM token_statuses
        WHERE filter_status = 'FAIL' AND prev_status = 'PASS'
        ORDER BY failed_at DESC
        LIMIT 100;
        """

        pass_to_fail = self.query_to_dataframe(pass_to_fail_query)

        if not pass_to_fail.empty:
            print(f"\n📉 Found {len(pass_to_fail)} PASS→FAIL transitions")
            print(f"   Average time to failure: {pass_to_fail['hours_to_failure'].mean():.1f} hours")
            print(f"   Median time to failure: {pass_to_fail['hours_to_failure'].median():.1f} hours")
            print(f"\n   Most common failure reasons:")

            # Explode array of reasons and count
            if 'filter_fail_reasons' in pass_to_fail.columns:
                all_reasons = pass_to_fail['filter_fail_reasons'].explode()
                reason_counts = all_reasons.value_counts().head(5)
                for reason, count in reason_counts.items():
                    print(f"      - {reason}: {count} times")

        # FAIL → PASS transitions
        fail_to_pass_query = """
        WITH token_statuses AS (
            SELECT
                token_address,
                snapshot_at,
                filter_status,
                LAG(filter_status) OVER (PARTITION BY token_address ORDER BY snapshot_at) as prev_status
            FROM time_series_data
            WHERE filter_status IS NOT NULL
        )
        SELECT
            token_address,
            snapshot_at as passed_at
        FROM token_statuses
        WHERE filter_status = 'PASS' AND prev_status = 'FAIL'
        ORDER BY passed_at DESC
        LIMIT 100;
        """

        fail_to_pass = self.query_to_dataframe(fail_to_pass_query)

        if not fail_to_pass.empty:
            print(f"\n📈 Found {len(fail_to_pass)} FAIL→PASS transitions (recoveries)")

        return {
            'pass_to_fail': pass_to_fail,
            'fail_to_pass': fail_to_pass
        }

    def analyze_price_performance(self) -> Dict:
        """
        Analyze price performance of PASS vs FAIL tokens

        Returns:
            Dict with performance statistics and DataFrames
        """
        print("\n" + "="*70)
        print("2. PRICE PERFORMANCE ANALYSIS")
        print("="*70)

        # Calculate ROI for PASS tokens
        pass_roi_query = """
        WITH pass_first AS (
            SELECT DISTINCT ON (token_address)
                token_address,
                snapshot_at as entry_time,
                price_usd as entry_price
            FROM time_series_data
            WHERE filter_status = 'PASS' AND price_usd > 0
            ORDER BY token_address, snapshot_at ASC
        ),
        pass_last AS (
            SELECT DISTINCT ON (token_address)
                token_address,
                snapshot_at as exit_time,
                price_usd as exit_price
            FROM time_series_data
            WHERE price_usd > 0
            ORDER BY token_address, snapshot_at DESC
        )
        SELECT
            p1.token_address,
            p1.entry_time,
            p2.exit_time,
            EXTRACT(EPOCH FROM (p2.exit_time - p1.entry_time)) / 3600 as hours_held,
            p1.entry_price,
            p2.exit_price,
            ((p2.exit_price - p1.entry_price) / p1.entry_price * 100) as roi_percent
        FROM pass_first p1
        JOIN pass_last p2 ON p1.token_address = p2.token_address
        WHERE p1.entry_price > 0 AND p2.exit_price > 0;
        """

        pass_performance = self.query_to_dataframe(pass_roi_query)

        if not pass_performance.empty:
            profitable = (pass_performance['roi_percent'] > 0).sum()
            win_rate = (profitable / len(pass_performance)) * 100
            tokens_2x = (pass_performance['roi_percent'] >= 100).sum()
            tokens_5x = (pass_performance['roi_percent'] >= 400).sum()
            tokens_10x = (pass_performance['roi_percent'] >= 900).sum()

            print(f"\n💰 PASS Token Performance:")
            print(f"   Total tokens: {len(pass_performance)}")
            print(f"   Win rate: {win_rate:.1f}% ({profitable}/{len(pass_performance)} profitable)")
            print(f"   Average ROI: {pass_performance['roi_percent'].mean():.1f}%")
            print(f"   Median ROI: {pass_performance['roi_percent'].median():.1f}%")
            print(f"   Best performer: {pass_performance['roi_percent'].max():.1f}%")
            print(f"   Worst performer: {pass_performance['roi_percent'].min():.1f}%")
            print(f"\n   Moonshots:")
            print(f"      2x+  : {tokens_2x} tokens ({tokens_2x/len(pass_performance)*100:.1f}%)")
            print(f"      5x+  : {tokens_5x} tokens ({tokens_5x/len(pass_performance)*100:.1f}%)")
            print(f"      10x+ : {tokens_10x} tokens ({tokens_10x/len(pass_performance)*100:.1f}%)")

            # Create ROI distribution plot
            self.plot_roi_distribution(pass_performance)

        return {
            'pass_performance': pass_performance
        }

    def analyze_legitimacy(self) -> pd.DataFrame:
        """
        Analyze token legitimacy (Real Project vs Meme vs Scam)

        Returns:
            DataFrame with legitimacy scores and classifications
        """
        print("\n" + "="*70)
        print("3. LEGITIMACY ANALYSIS")
        print("="*70)

        legitimacy_query = """
        WITH token_first AS (
            SELECT DISTINCT ON (token_address)
                token_address,
                liquidity_usd as first_liquidity,
                holder_count as first_holders,
                volume_24h as first_volume
            FROM time_series_data
            ORDER BY token_address, snapshot_at ASC
        ),
        token_latest AS (
            SELECT DISTINCT ON (token_address)
                token_address,
                liquidity_usd as latest_liquidity,
                holder_count as latest_holders,
                volume_24h as latest_volume,
                buys_24h,
                sells_24h
            FROM time_series_data
            ORDER BY token_address, snapshot_at DESC
        )
        SELECT
            f.token_address,
            f.first_liquidity,
            l.latest_liquidity,
            ((l.latest_liquidity - f.first_liquidity) / NULLIF(f.first_liquidity, 0) * 100) as liquidity_growth_pct,
            f.first_holders,
            l.latest_holders,
            ((l.latest_holders - f.first_holders) / NULLIF(f.first_holders::float, 0) * 100) as holder_growth_pct,
            CASE
                WHEN l.buys_24h + l.sells_24h > 0
                THEN (l.buys_24h::float / (l.buys_24h + l.sells_24h) * 100)
                ELSE NULL
            END as buy_pressure_pct,
            CASE
                WHEN l.latest_liquidity > f.first_liquidity * 2 AND l.latest_holders > f.first_holders * 1.5
                THEN 'Real Project'
                WHEN l.latest_liquidity < f.first_liquidity * 0.5
                THEN 'Likely Scam'
                ELSE 'Meme/Speculative'
            END as classification
        FROM token_first f
        JOIN token_latest l ON f.token_address = l.token_address
        WHERE f.first_liquidity > 0;
        """

        legitimacy = self.query_to_dataframe(legitimacy_query)

        if not legitimacy.empty:
            classification_counts = legitimacy['classification'].value_counts()
            print(f"\n🔍 Token Classification:")
            for classification, count in classification_counts.items():
                pct = (count / len(legitimacy)) * 100
                print(f"   {classification}: {count} ({pct:.1f}%)")

            # Top real projects
            real_projects = legitimacy[legitimacy['classification'] == 'Real Project'].sort_values(
                'liquidity_growth_pct', ascending=False
            ).head(10)

            if not real_projects.empty:
                print(f"\n🏆 Top 10 Real Projects (by liquidity growth):")
                for idx, row in real_projects.iterrows():
                    print(f"   {row['token_address'][:10]}... : +{row['liquidity_growth_pct']:.0f}% liquidity, +{row['holder_growth_pct']:.0f}% holders")

        return legitimacy

    def analyze_filter_effectiveness(self) -> Dict:
        """
        Analyze which filters are most effective

        Returns:
            Dict with filter effectiveness metrics
        """
        print("\n" + "="*70)
        print("4. FILTER EFFECTIVENESS ANALYSIS")
        print("="*70)

        # Overall metrics
        overall_query = """
        WITH all_tokens AS (
            SELECT DISTINCT token_address FROM time_series_data
        ),
        ever_passed AS (
            SELECT DISTINCT token_address FROM time_series_data WHERE filter_status = 'PASS'
        ),
        profitable_tokens AS (
            SELECT token_address
            FROM (
                SELECT
                    token_address,
                    MIN(price_usd) as min_price,
                    MAX(price_usd) as max_price
                FROM time_series_data
                GROUP BY token_address
            ) ranges
            WHERE max_price > min_price * 1.5
        )
        SELECT
            (SELECT COUNT(*) FROM all_tokens) as total_tokens,
            (SELECT COUNT(*) FROM ever_passed) as passed_tokens,
            (SELECT COUNT(*) FROM profitable_tokens) as profitable_tokens,
            (SELECT COUNT(DISTINCT ep.token_address)
             FROM ever_passed ep
             JOIN profitable_tokens pt ON ep.token_address = pt.token_address
            ) as profitable_passed_tokens;
        """

        overall = self.query_to_dataframe(overall_query)

        if not overall.empty:
            row = overall.iloc[0]
            precision = (row['profitable_passed_tokens'] / row['passed_tokens'] * 100) if row['passed_tokens'] > 0 else 0
            recall = (row['profitable_passed_tokens'] / row['profitable_tokens'] * 100) if row['profitable_tokens'] > 0 else 0

            print(f"\n📊 Overall Filter Performance:")
            print(f"   Total tokens tracked: {row['total_tokens']}")
            print(f"   Tokens that passed filters: {row['passed_tokens']}")
            print(f"   Profitable tokens (1.5x+): {row['profitable_tokens']}")
            print(f"   Profitable tokens that passed: {row['profitable_passed_tokens']}")
            print(f"\n   Precision: {precision:.1f}% (when we say PASS, it's profitable {precision:.1f}% of the time)")
            print(f"   Recall: {recall:.1f}% (we catch {recall:.1f}% of all profitable tokens)")

        return {
            'overall_metrics': overall
        }

    def plot_roi_distribution(self, performance_df: pd.DataFrame):
        """Create ROI distribution histogram"""
        plt.figure(figsize=(12, 6))

        # Clip extreme values for better visualization
        roi_clipped = performance_df['roi_percent'].clip(-100, 500)

        plt.hist(roi_clipped, bins=50, color='#2ecc71', alpha=0.7, edgecolor='black')
        plt.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Break-even')
        plt.axvline(x=performance_df['roi_percent'].median(), color='blue',
                    linestyle='--', linewidth=2, label=f'Median: {performance_df["roi_percent"].median():.1f}%')

        plt.xlabel('ROI %', fontsize=12)
        plt.ylabel('Number of Tokens', fontsize=12)
        plt.title('PASS Token ROI Distribution', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)

        output_path = f"{self.output_dir}/roi_distribution.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n📊 Saved ROI distribution chart: {output_path}")
        plt.close()

    def export_reports(self, results: Dict):
        """Export analysis results to CSV files"""
        print("\n" + "="*70)
        print("EXPORTING REPORTS")
        print("="*70)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for name, df in results.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                filename = f"{self.output_dir}/{name}_{timestamp}.csv"
                df.to_csv(filename, index=False)
                print(f"✅ Exported: {filename} ({len(df)} rows)")

    def run_full_analysis(self):
        """Run complete analysis suite"""
        print("\n" + "="*70)
        print("🚀 SUPER PANCAKE - TOKEN PERFORMANCE ANALYSIS")
        print("="*70)
        print(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        results = {}

        try:
            # Run all analyses
            transitions = self.analyze_filter_transitions()
            results.update(transitions)

            performance = self.analyze_price_performance()
            results.update(performance)

            legitimacy = self.analyze_legitimacy()
            results['legitimacy_scores'] = legitimacy

            effectiveness = self.analyze_filter_effectiveness()
            results.update(effectiveness)

            # Export all results
            self.export_reports(results)

            print("\n" + "="*70)
            print("✅ ANALYSIS COMPLETE")
            print("="*70)
            print(f"Results saved to: {self.output_dir}/")

        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            raise

        finally:
            self.engine.dispose()
            print("\n🔌 Database connection closed")


def main():
    """Main entry point"""
    try:
        analyzer = TokenAnalyzer()
        analyzer.run_full_analysis()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
