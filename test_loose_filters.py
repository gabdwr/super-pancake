"""
Test script with LOOSE filters to see what's out there
This shows you what tokens exist before heavy filtering
"""

from src.discovery.dexscreener import Dexscreener

def test_loose():
    api = Dexscreener()

    print("🔍 LOOSE Filter Test - See What We're Missing")
    print("=" * 70)

    # MUCH looser filters
    tokens = api.discover_latest_bsc_tokens_enhanced(
        min_liquidity_usd=5000,      # Half of normal
        max_age_days=60,              # Double the age range
        limit=50,
        min_liquidity_score=60,       # Lower quality threshold
        trade_size_usd=50
    )

    print(f"\n✅ Found {len(tokens)} tokens with LOOSE filters")
    print("=" * 70)

    # Count by score
    scores = {}
    for pair in tokens:
        liq = pair.get('liquidity_analysis')
        if liq:
            score = liq['total_score']
            bucket = (score // 10) * 10  # Round to nearest 10
            scores[bucket] = scores.get(bucket, 0) + 1

    print("\n📊 Score Distribution:")
    for bucket in sorted(scores.keys(), reverse=True):
        count = scores[bucket]
        bar = "█" * count
        print(f"   {bucket}-{bucket+9}: {bar} ({count})")

    print("\n🎯 Top 10 by Liquidity Score:")
    sorted_tokens = sorted(
        tokens,
        key=lambda x: x.get('liquidity_analysis', {}).get('total_score', 0),
        reverse=True
    )

    for i, pair in enumerate(sorted_tokens[:10], 1):
        token_info = api.extract_token_info(pair)
        liq = token_info.get('liquidity_analysis', {})

        print(f"\n#{i} - {token_info['name']} (${token_info['symbol']})")
        print(f"   Score: {liq.get('total_score', 0)}/100")
        print(f"   Liquidity: ${token_info['liquidity_usd']:,.0f}")
        print(f"   Market Cap: ${token_info['market_cap']:,.0f}")
        print(f"   Age: {token_info.get('age_days', '?')} days")
        print(f"   Recommendation: {liq.get('recommendation', 'N/A')}")

    print("\n" + "=" * 70)
    print("💡 Compare this to your strict filters!")
    print("   Strict filters (score ≥80): Would get ~" +
          str(scores.get(80, 0) + scores.get(90, 0)) + " tokens")
    print("   Loose filters (score ≥60): Got " + str(len(tokens)) + " tokens")

if __name__ == "__main__":
    test_loose()
