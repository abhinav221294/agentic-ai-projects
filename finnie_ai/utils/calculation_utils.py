def calculate_sip_future_value(monthly_investment, annual_return=10, years=10):
    """
    Calculate future value of SIP
    """
    r = annual_return / 100 / 12   # monthly rate
    n = years * 12

    fv = monthly_investment * (((1 + r)**n - 1) / r) * (1 + r)
    return int(fv)

def calculate_lumpsum_future_value(principal, annual_return=10, years=10):
    r = annual_return / 100
    fv = principal * ((1 + r) ** years)
    return int(fv)