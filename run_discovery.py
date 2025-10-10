import os
from src.discovery.old_dexscreener import Dexscreener
from src.utils.telegram_alerts import get_telegram_alert

def test_dandl():
    api = Dexscreener()
    telegram = get_telegram_alert()
    send_telegram = False # Make this True if you want to enable alerts

    # Load filter settings from environment (or use defaults)
    min_liquidity = int(os.getenv('DISCOVERY_MIN_LIQUIDITY', '10000'))
    max_age_days = int(os.getenv('DISCOVERY_MAX_AGE_DAYS', '30'))
    min_score = int(os.getenv('DISCOVERY_MIN_SCORE', '80'))
    alert_threshold = int(os.getenv('DISCOVERY_ALERT_THRESHOLD', '60'))

    # Send script start notification
    if send_telegram:
        telegram.send_script_start_alert(
            script_name="Token Discovery & Liquidity Analysis",
            filters={
                "Min Liquidity": f"${min_liquidity:,}",
                "Max Age": f"{max_age_days} days",
                "Min Score": f"{min_score}/100",
                "Alert Threshold": f"{alert_threshold}/100"
            }
        )

    # Test: Discover latest BSC tokens
    print("Test: Discover Latest BSC Tokens")
    print("-" * 70)
    print(f"Filters: Liquidity ${min_liquidity:,} | Age {max_age_days}d | Score {min_score}+ | Alerts {alert_threshold}+")
    print("-" * 70)
    tokens = api.discover_latest_bsc_tokens_enhanced(
        min_liquidity_usd=min_liquidity,
        max_age_days=max_age_days,
        min_liquidity_score=min_score
    )
    print(f"Top {len(tokens)} Recent BSC Tokens:")
    print("=" * 70)
    # Track tokens that pass filters for summary
    tokens_passed_filters = 0

    for i, pair in enumerate(tokens, 1):
        token_info = api.extract_token_info(pair)
        if token_info:
            print(f"\n#{i} - {token_info['name']} (${token_info['symbol']})")
            print(f"   Address: {token_info['address']}")
            if token_info['age_days'] is not None:
                print(f"   Age: {token_info['age_days']} days ({token_info['age_hours']:.1f} hours)")
            else:
                print("   Age: Unknown")
            print(f"   Liquidity: ${token_info['liquidity_usd']:,.2f}")
            print(f"   Market Cap: ${token_info['market_cap']:,.2f}")
            print(f"   24h Volume: ${token_info['volume_24h']:,.2f}")
            print(f"   24h Change: {token_info['price_change_24h']:.2f}%")
            print(f"   DEX: {token_info['dex']}")
            print(f"   URL: {token_info['url']}")
            if token_info['liquidity_analysis'] is not None:
                liq = token_info['liquidity_analysis']
                print("\n   LIQUIDITY ANALYSIS:")
                print(f"      Score: {liq['total_score']}/100 - {liq['recommendation']}")

                # Concentration
                conc = liq['analysis']['concentration']
                print(f"      Concentration: {conc['concentration_ratio']:.1%} ({conc['pair_count']} pairs) - {conc['flag']}")

                # Lock status
                lock = liq['analysis']['lock']
                if lock['is_locked']:
                    print(f"      Lock: {lock['locked_percentage']:.1f}% locked ({lock['locker_name']}) - {lock['flag']}")
                else:
                    print(f"      Lock: Not locked - {lock['flag']}")

                # Wash trading
                wash = liq['analysis']['wash_trading']
                print(f"      Wash Trading: {wash['volume_liquidity_ratio']:.2f} ratio - {wash['flag']}")

                # Slippage
                slip = liq['analysis']['slippage']
                print(f"      Slippage: {slip['estimated_slippage_percent']:.3f}% for ${slip['trade_size_usd']} - {slip['flag']}")

                # Rugpull risk
                rug = liq['analysis']['rugpull']
                print(f"      Rugpull Risk: {rug['risk_score']} - {rug['flag']}")

                # Flags
                if liq['flags']:
                    print(f"      Flags: {', '.join(liq['flags'])}")

                # Send Telegram alert for tokens that pass alert threshold
                if send_telegram:
                    if liq['total_score'] >= alert_threshold:
                        tokens_passed_filters += 1

                        # Different emoji based on score
                        if liq['total_score'] >= 80:
                            status = "✅ SAFE"
                        elif liq['total_score'] >= 70:
                            status = "⚠️ CAUTION"
                        else:
                            status = "🔶 RISKY"

                        print(f"\n   📱 Sending Telegram alert ({status})...")
                        telegram.send_token_discovery_alert(token_info)

    print("\n" + "=" * 70)
    print("✅ All tests complete!")

    # Send completion summary
    if send_telegram:
        telegram.send_script_complete_alert(
            script_name="Token Discovery & Liquidity Analysis",
            tokens_found=len(tokens),
            tokens_passed=tokens_passed_filters
        )

if __name__ == "__main__":
    test_dandl()