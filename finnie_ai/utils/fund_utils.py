from difflib import get_close_matches
from utils.finance_constants import ASSET_MAP,MAX_LIMITS
import re


def extract_user_allocation(query):
    allocation = {}
    unknown_assets = []

    query = query.lower()

    # ✅ support both formats
    pattern1 = r"(\d+)%?\s*([a-zA-Z ]+)"   # 100 crypto / 100% crypto
    pattern2 = r"([a-zA-Z ]+)\s*(\d+)%?"   # crypto 100 / crypto 100%

    matches1 = re.findall(pattern1, query)
    matches2 = re.findall(pattern2, query)

    def map_asset(asset_raw, percent):
        asset_raw = asset_raw.strip().lower()
        percent = int(percent)

        for canonical, aliases in ASSET_MAP.items():
            all_terms = aliases + [canonical]

            match = get_close_matches(asset_raw, all_terms, n=1, cutoff=0.7)

            if match:
                allocation[canonical] = allocation.get(canonical, 0) + percent
                return True
        return False

    # format: 100 crypto
    for percent, asset in matches1:
        if not map_asset(asset, percent):
            unknown_assets.append(asset.strip())

    # format: crypto 100
    for asset, percent in matches2:
        if not map_asset(asset, percent):
            unknown_assets.append(asset.strip())

    # remove duplicates
    unknown_assets = list(set(unknown_assets))
    return allocation, unknown_assets


def merge_allocation(user_alloc, default_alloc):
    result = {}

    total_user = sum(user_alloc.values())
    remaining = 100 - total_user

    # ❌ invalid case
    if remaining < 0:
        return None

    # assets not provided by user
    remaining_assets = [k for k in default_alloc if k not in user_alloc]

    default_remaining_sum = sum(default_alloc[k] for k in remaining_assets)

    # ⚠️ edge case: user defined everything
    if default_remaining_sum == 0:
        return user_alloc

    # distribute remaining %
    for asset in default_alloc:
        if asset in user_alloc:
            result[asset] = user_alloc[asset]
        else:
            weight = default_alloc[asset] / default_remaining_sum
            result[asset] = round(weight * remaining)

    # include extra assets (like crypto)
    for asset in user_alloc:
        if asset not in result:
            result[asset] = user_alloc[asset]

    # ✅ normalize to 100
    total = sum(result.values())

    if total != 100:
        diff = 100 - total

        for k in result:
            if k not in MAX_LIMITS:
                result[k] += diff
                break

    return result