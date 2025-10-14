"""
Graduation System for Smart API Caching

This module implements a "5-Pass Graduation" system to reduce GoPlus API usage:

1. New tokens → Checked every hour (full GoPlus + DexScreener)
2. After 5 consecutive PASS → "Graduated" → GoPlus checked only 1x/day
3. Graduated tokens → DexScreener still checked hourly (liquidity/volume monitoring)
4. If graduated token fails → Demoted back to hourly checking

Expected API savings: 80% reduction in GoPlus calls after tokens graduate
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# Graduation constants
PASSES_TO_GRADUATE = 5  # Number of consecutive passes required to graduate
GRADUATED_CHECK_INTERVAL_HOURS = 24  # Check graduated tokens once per day
DAILY_REFRESH_HOUR = 3  # UTC hour for daily GoPlus refresh (3am UTC = off-peak)


def should_fetch_goplus(token_data: Dict, current_hour: int = None) -> bool:
    """
    Determine if we need to fetch fresh GoPlus data for this token.

    Args:
        token_data: Token record from discovered_tokens table
        current_hour: Current UTC hour (0-23), defaults to datetime.now()

    Returns:
        True if GoPlus API should be called, False if cached data should be used
    """
    graduated = token_data.get('graduated', False)

    # Non-graduated tokens: always fetch GoPlus
    if not graduated:
        return True

    # Graduated tokens: check if 24h has passed OR it's daily refresh hour
    last_check = token_data.get('last_goplus_check')

    if not last_check:
        # No record of last check, fetch now
        return True

    # Parse last check timestamp
    if isinstance(last_check, str):
        last_check = datetime.fromisoformat(last_check.replace('Z', '+00:00'))

    # Calculate hours since last check
    hours_since_check = (datetime.now() - last_check).total_seconds() / 3600

    # Fetch if 24+ hours passed
    if hours_since_check >= GRADUATED_CHECK_INTERVAL_HOURS:
        logger.info(f"🔄 Graduated token due for refresh ({hours_since_check:.1f}h since last check)")
        return True

    # Also fetch during daily refresh hour (even if <24h)
    if current_hour is None:
        current_hour = datetime.now().hour

    if current_hour == DAILY_REFRESH_HOUR and hours_since_check >= 1:
        logger.info(f"🔄 Daily refresh hour ({DAILY_REFRESH_HOUR}:00 UTC)")
        return True

    # Otherwise, use cached data
    logger.info(f"📦 Using cached GoPlus data (last check: {hours_since_check:.1f}h ago)")
    return False


def update_graduation_status(
    token_address: str,
    current_status: Dict,
    filter_status: str
) -> Tuple[bool, int, str]:
    """
    Update token graduation status based on filter result.

    Graduation rules:
    - PASS: Increment consecutive_passes
    - After 5 consecutive PASS: Graduate token
    - FAIL: Reset consecutive_passes to 0, demote if graduated

    Args:
        token_address: Token contract address
        current_status: Current graduation status {graduated, consecutive_passes}
        filter_status: Current filter result ('PASS' or 'FAIL')

    Returns:
        Tuple of (graduated, consecutive_passes, action)
        action: 'GRADUATED', 'DEMOTED', 'PROGRESS', or 'NO_CHANGE'
    """
    graduated = current_status.get('graduated', False)
    consecutive_passes = current_status.get('consecutive_passes', 0)

    if filter_status == 'PASS':
        consecutive_passes += 1

        # Graduate after PASSES_TO_GRADUATE consecutive passes
        if consecutive_passes >= PASSES_TO_GRADUATE and not graduated:
            graduated = True
            action = 'GRADUATED'
            logger.info(
                f"🎓 Token {token_address} GRADUATED "
                f"({consecutive_passes} consecutive passes, GoPlus → daily)"
            )
        else:
            action = 'PROGRESS' if not graduated else 'NO_CHANGE'
            if not graduated:
                logger.debug(
                    f"✅ Token {token_address} pass #{consecutive_passes}/{PASSES_TO_GRADUATE} "
                    f"({PASSES_TO_GRADUATE - consecutive_passes} more to graduate)"
                )

    elif filter_status == 'FAIL':
        # Reset consecutive passes on failure
        if consecutive_passes > 0 or graduated:
            old_graduated = graduated
            old_passes = consecutive_passes

            consecutive_passes = 0
            graduated = False

            if old_graduated:
                action = 'DEMOTED'
                logger.warning(
                    f"⚠️ Token {token_address} DEMOTED "
                    f"(failed after graduation, GoPlus → hourly)"
                )
            else:
                action = 'PROGRESS'
                logger.debug(
                    f"❌ Token {token_address} failed, streak reset "
                    f"(was at {old_passes}/{PASSES_TO_GRADUATE})"
                )
        else:
            action = 'NO_CHANGE'

    else:
        # Unknown filter status, no change
        action = 'NO_CHANGE'

    return graduated, consecutive_passes, action


def get_graduation_summary(all_tokens: list) -> Dict:
    """
    Generate summary statistics about graduation status.

    Args:
        all_tokens: List of all token records from discovered_tokens

    Returns:
        Dict with graduation statistics
    """
    total = len(all_tokens)
    graduated = sum(1 for t in all_tokens if t.get('graduated', False))
    in_progress = sum(
        1 for t in all_tokens
        if not t.get('graduated', False) and t.get('consecutive_passes', 0) > 0
    )
    new = total - graduated - in_progress

    return {
        'total_tokens': total,
        'graduated': graduated,
        'in_progress': in_progress,
        'new': new,
        'graduation_rate': round((graduated / total * 100), 1) if total > 0 else 0,
        'estimated_daily_goplus_calls': (new * 24) + (in_progress * 24) + graduated
    }
