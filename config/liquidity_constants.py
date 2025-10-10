"""
Liquidity Analysis Constants and Thresholds

Contains known contract addresses for liquidity lockers, dead addresses,
and threshold values for liquidity quality assessment.
"""

# Known liquidity locker contracts on BSC
LIQUIDITY_LOCKERS = {
    # UNCX Network
    '0xc765bddb93b0d1c1a88282ba0fa6b2d00e3e0c83': {
        'name': 'UNCX Network V1',
        'verified': True,
        'website': 'https://uncx.network'
    },
    '0x231278edd38b00b07fbd52120cef685b9baebcc1': {
        'name': 'UNCX Network V2',
        'verified': True,
        'website': 'https://uncx.network'
    },

    # PinkLock (Pinksale)
    '0x407993575c91ce7643a4d4ccacc9a98c36ee1bbe': {
        'name': 'PinkLock V1',
        'verified': True,
        'website': 'https://www.pinksale.finance'
    },
    '0x71b5759d73262fbb223956913ecf4ecc51057641': {
        'name': 'PinkLock V2',
        'verified': True,
        'website': 'https://www.pinksale.finance'
    },

    # Team Finance
    '0x3f4d6bf08cb7a003488ef082102c2e6418a4551e': {
        'name': 'Team Finance',
        'verified': True,
        'website': 'https://www.team.finance'
    },

    # TrustSwap
    '0x9a6d6a0bb0a06dae58b5b3d8b4b4f4e5d8e8b5a5': {
        'name': 'TrustSwap',
        'verified': True,
        'website': 'https://trustswap.org'
    },

    # CryptEx Locker
    '0x2f7f7e3e89c4b11b0d7a3c3a1e1a4d7f5e6c3b2a': {
        'name': 'CryptEx Locker',
        'verified': True,
        'website': 'https://cryptexlock.me'
    },

    # Mudra Locker
    '0x8e5c0e21c3b2e3e1e9a4e0e3e4e5e6e7e8e9e0e1': {
        'name': 'Mudra Locker',
        'verified': True,
        'website': 'https://mudra.website'
    }
}

# Dead/burn addresses where LP tokens are often sent
DEAD_ADDRESSES = {
    '0x000000000000000000000000000000000000dead': 'Dead address',
    '0x0000000000000000000000000000000000000000': 'Zero address',
    '0x000000000000000000000000000000000000dEaD': 'Dead address (checksum)',
}

# Liquidity concentration thresholds
CONCENTRATION_THRESHOLDS = {
    'HEALTHY': 0.8,      # >80% in main pair = healthy
    'CAUTION': 0.5,      # 50-80% = needs review
    'RED_FLAG': 0.5      # <50% = fragmented, likely scam
}

# Liquidity lock thresholds (percentage of LP tokens locked)
LOCK_THRESHOLDS = {
    'LOCKED': 80,        # >80% locked = safe
    'PARTIAL': 30,       # 30-80% = partial lock
    'UNLOCKED': 30       # <30% = not locked
}

# LP holder distribution thresholds
LP_HOLDER_THRESHOLDS = {
    'TOP_HOLDER_MAX': 30,          # Top holder should have <30%
    'TOP_10_HOLDERS_MAX': 70,      # Top 10 should have <70%
    'MIN_HOLDER_COUNT': 10,        # At least 10 holders
    'GINI_COEFFICIENT_MAX': 0.7    # Gini <0.7 (lower = more distributed)
}

# Volume/Liquidity ratio thresholds (wash trading detection)
WASH_TRADING_THRESHOLDS = {
    'HEALTHY_MIN': 0.5,     # Minimum healthy ratio
    'HEALTHY_MAX': 3.0,     # Maximum healthy ratio
    'SUSPICIOUS': 5.0,      # >5.0 = suspicious
    'WASH_TRADING': 10.0    # >10.0 = very likely wash trading
}

# Slippage thresholds (percentage)
SLIPPAGE_THRESHOLDS = {
    'LOW': 1.0,          # <1% = low slippage
    'MEDIUM': 5.0,       # 1-5% = medium
    'HIGH': 5.0          # >5% = high slippage
}

# Minimum liquidity thresholds (USD)
MIN_LIQUIDITY_THRESHOLDS = {
    'SAFE': 50000,       # >$50k = safe to trade
    'CAUTION': 10000,    # $10k-50k = trade with caution
    'DANGEROUS': 10000   # <$10k = dangerous
}

# Rugpull pattern risk scores
RUGPULL_RISK_SCORES = {
    'HIDDEN_HIGH_TAX': 40,           # Buy/sell tax >25%
    'OWNERSHIP_NOT_RENOUNCED': 20,   # Owner can still modify contract
    'PROXY_CONTRACT': 30,            # Upgradeable contract
    'LOW_LIQUIDITY': 30,             # <$10k liquidity
    'VERY_LOW_LIQUIDITY': 50,        # <$1k liquidity
    'SINGLE_LARGE_HOLDER': 25,       # One holder has >50%
    'NEW_TOKEN_NO_LOCK': 35,         # <7 days old with no lock
    'CONCENTRATED_HOLDERS': 20,      # Top 10 holders >90%
    'SUSPICIOUS_CONTRACT': 40        # Malicious functions detected
}

# Comprehensive scoring weights
SCORING_WEIGHTS = {
    'lock_verification': 30,      # 30 points max
    'concentration': 20,          # 20 points max
    'lp_distribution': 15,        # 15 points max
    'wash_trading': 15,           # 15 points max
    'migration': 10,              # 10 points max
    'slippage': 10                # 10 points max
    # Total: 100 points
}

# Recommendation thresholds
RECOMMENDATION_THRESHOLDS = {
    'PASS': 80,          # >=80 = PASS
    'CAUTION': 60,       # 60-79 = CAUTION
    'REJECT': 60         # <60 = REJECT
}

# Time windows for analysis
TIME_WINDOWS = {
    'MIGRATION_CHECK_DAYS': 30,       # Check for migrations in last 30 days
    'VOLUME_WINDOW_HOURS': 24,        # Use 24h volume for analysis
    'NEW_TOKEN_DAYS': 7,              # Tokens <7 days are "new"
    'EARLY_TOKEN_DAYS': 30            # Tokens <30 days are "early"
}

# API rate limiting
RATE_LIMITS = {
    'DEXSCREENER_DELAY': 0.2,        # 200ms between requests
    'BSCSCAN_DELAY': 0.25,           # 250ms between requests
    'MORALIS_DELAY': 0.1             # 100ms between requests
}

# Contract ABIs (minimal, for specific functions)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

PAIR_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token1",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"name": "reserve0", "type": "uint112"},
            {"name": "reserve1", "type": "uint112"},
            {"name": "blockTimestampLast", "type": "uint32"}
        ],
        "type": "function"
    }
]

# Known scam indicators (addresses, patterns)
KNOWN_SCAM_INDICATORS = {
    'suspicious_contract_names': [
        'honeypot',
        'scam',
        'test',
        'fake',
        'rug'
    ],
    'suspicious_symbols': [
        'TEST',
        'SCAM',
        'FAKE'
    ]
}
