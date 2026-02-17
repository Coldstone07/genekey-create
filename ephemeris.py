"""Swiss Ephemeris wrapper for planetary position calculations."""

import swisseph as swe
from datetime import datetime, timedelta


# Planet constants from pyswisseph
SUN = swe.SUN
MOON = swe.MOON
MERCURY = swe.MERCURY
VENUS = swe.VENUS
MARS = swe.MARS
JUPITER = swe.JUPITER
SATURN = swe.SATURN


def datetime_to_jd(dt):
    """Convert a datetime object to Julian Day number."""
    return swe.julday(dt.year, dt.month, dt.day,
                      dt.hour + dt.minute / 60.0 + dt.second / 3600.0)


def get_planet_longitude(jd, planet):
    """Get the ecliptic longitude of a planet at a given Julian Day."""
    result, _ = swe.calc_ut(jd, planet)
    return result[0]  # longitude in degrees


def get_planetary_positions(dt):
    """Get longitudes for all relevant planets at a given datetime (UTC).

    Returns dict mapping planet ID to longitude in degrees.
    """
    jd = datetime_to_jd(dt)
    planets = [SUN, MOON, VENUS, MARS, JUPITER]
    positions = {}
    for planet in planets:
        positions[planet] = get_planet_longitude(jd, planet)
    # Earth is opposite the Sun
    positions['EARTH'] = (positions[SUN] + 180.0) % 360.0
    return positions


def find_design_date(birth_dt):
    """Find the 'design date' — when the Sun was exactly 88 degrees
    before the birth Sun position.

    Uses binary search scanning ~84-96 days before birth.
    """
    birth_jd = datetime_to_jd(birth_dt)
    birth_sun = get_planet_longitude(birth_jd, SUN)

    # Target: Sun longitude that is 88 degrees behind birth Sun
    target_sun = (birth_sun - 88.0) % 360.0

    # Search window: roughly 84 to 96 days before birth
    early_dt = birth_dt - timedelta(days=96)
    late_dt = birth_dt - timedelta(days=84)

    early_jd = datetime_to_jd(early_dt)
    late_jd = datetime_to_jd(late_dt)

    def angle_diff(jd):
        """Signed angular difference from target (handles 360° wrap)."""
        sun_lon = get_planet_longitude(jd, SUN)
        diff = sun_lon - target_sun
        # Normalize to [-180, 180]
        while diff > 180:
            diff -= 360
        while diff < -180:
            diff += 360
        return diff

    # Binary search for the zero crossing
    for _ in range(64):  # 64 iterations gives sub-second precision
        mid_jd = (early_jd + late_jd) / 2.0
        diff = angle_diff(mid_jd)
        if diff < 0:
            early_jd = mid_jd
        else:
            late_jd = mid_jd

    # Convert result back to datetime
    design_jd = (early_jd + late_jd) / 2.0
    # Use swe to convert JD back
    year, month, day, hour_frac = swe.revjul(design_jd)
    hours = int(hour_frac)
    minutes = int((hour_frac - hours) * 60)
    seconds = int(((hour_frac - hours) * 60 - minutes) * 60)
    return datetime(year, month, day, hours, minutes, seconds)
