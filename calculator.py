"""Gene Key gate mapping and hologenetic profile calculation."""

from datetime import datetime
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import zoneinfo

from ephemeris import (
    get_planetary_positions, find_design_date,
    SUN, MOON, VENUS, MARS, JUPITER
)

# The 64 gates in zodiacal order (starting from 0° Aries + 58° offset)
GATES = [
    41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3,
    27, 24, 2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56,
    31, 33, 7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50,
    28, 44, 1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60
]


def longitude_to_gate_line(longitude):
    """Convert ecliptic longitude to Gene Key gate number and line.

    The zodiacal I Ching wheel starts at 58° offset from 0° Aries.
    Each of the 64 gates spans 5.625° (360/64).
    Each gate has 6 lines, each spanning 0.9375° (5.625/6).
    """
    adjusted = (longitude + 58.0) % 360.0
    percentage = adjusted / 360.0
    gate_index = int(percentage * 64)
    gate = GATES[gate_index % 64]
    line = int((percentage * 384) % 6) + 1
    return gate, line


# Sphere definitions: (planet, side)
# side = 'personality' (birth) or 'design' (prenatal)
SPHERES = {
    # Activation Sequence
    "Life's Work": (SUN, 'personality'),
    "Evolution":   ('EARTH', 'personality'),
    "Radiance":    (SUN, 'design'),
    "Purpose":     ('EARTH', 'design'),
    # Venus Sequence
    "Attraction":  (MOON, 'design'),
    "IQ":          (VENUS, 'personality'),
    "EQ":          (MARS, 'personality'),
    "SQ":          (VENUS, 'design'),
    "Vocation":    (MARS, 'design'),
    # Pearl Sequence
    "Culture":     (JUPITER, 'design'),
    "Pearl":       (JUPITER, 'personality'),
}

SEQUENCES = {
    "Activation Sequence": ["Life's Work", "Evolution", "Radiance", "Purpose"],
    "Venus Sequence": ["Attraction", "IQ", "EQ", "SQ", "Vocation"],
    "Pearl Sequence": ["Culture", "Pearl"],
}


def location_to_coords(location_str):
    """Convert a location string to (latitude, longitude) using geocoding."""
    geolocator = Nominatim(user_agent="genekeys_calculator")
    loc = geolocator.geocode(location_str)
    if loc is None:
        raise ValueError(f"Could not geocode location: {location_str}")
    return loc.latitude, loc.longitude


def to_utc(date_str, time_str, lat, lon):
    """Convert local date/time at given coordinates to UTC datetime."""
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon)
    if tz_name is None:
        raise ValueError(f"Could not determine timezone for ({lat}, {lon})")

    local_tz = zoneinfo.ZoneInfo(tz_name)
    # Parse date and time
    date_parts = date_str.split('-')
    year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
    time_parts = time_str.split(':')
    hour, minute = int(time_parts[0]), int(time_parts[1])

    local_dt = datetime(year, month, day, hour, minute, tzinfo=local_tz)
    utc_dt = local_dt.astimezone(zoneinfo.ZoneInfo('UTC'))
    return utc_dt.replace(tzinfo=None)  # return naive UTC datetime


def _build_profile(date_str, time_str, lat, lon):
    """Core profile calculation from coordinates (no geocoding)."""
    birth_utc = to_utc(date_str, time_str, lat, lon)

    personality_positions = get_planetary_positions(birth_utc)
    design_dt = find_design_date(birth_utc)
    design_positions = get_planetary_positions(design_dt)

    profile = {}
    for sphere_name, (planet, side) in SPHERES.items():
        positions = personality_positions if side == 'personality' else design_positions
        longitude = positions[planet]
        gate, line = longitude_to_gate_line(longitude)
        profile[sphere_name] = {"gate": gate, "line": line}

    return profile


def calculate_profile_from_coords(date_str, time_str, lat, lon):
    """Calculate profile directly from coordinates (used by the API)."""
    return _build_profile(date_str, time_str, lat, lon)


def calculate_profile(date_str, time_str="12:00", location_str="Greenwich, UK"):
    """Calculate profile from a location string (used by CLI)."""
    lat, lon = location_to_coords(location_str)
    return _build_profile(date_str, time_str, lat, lon)
