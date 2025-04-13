def calculate_net_efficiency(panel_efficiency, system_loss):
    """
    Calculate net panel efficiency after losses.
    """
    return panel_efficiency * (1 - system_loss)


def estimate_energy(area_m2, irradiance_kwh_per_m2_day, panel_efficiency, system_loss):
    """
    Estimate daily and yearly energy output from panel area.
    """
    net_efficiency = calculate_net_efficiency(panel_efficiency, system_loss)
    daily_energy_kwh = area_m2 * irradiance_kwh_per_m2_day * net_efficiency
    yearly_energy_kwh = daily_energy_kwh * 365
    return daily_energy_kwh, yearly_energy_kwh
