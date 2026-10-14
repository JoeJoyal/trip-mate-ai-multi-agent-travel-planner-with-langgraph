import os
import re
import requests
import certifi
import airportsdata
import pycountry
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# CONFIGURE SSL CERTIFICATES
# ============================================================
# Get the path to the trusted CA certificate bundle provided by certifi.
# This helps Python verify the identity of HTTPS servers.

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA-BUNDLE"] = certifi.where()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

# ============================================================
# CONFIGURE THE DEFAULT DEPARTURE AIRPORT
# ============================================================

# Read the default departure airport's IATA code from the .env file.
# If the variable is missing, use DAC (Dhaka, Bangladesh).
# Example: If a user says "Plan a trip to Japan" without specifying
# a departure city, the application can use this default airport.

DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN_IATA", "DAC")

# ============================================================
# DEFINE THE FLIGHT SEARCH API ENDPOINT
# ============================================================

# Store the Aviationstack API URL used to retrieve flight information.
BASE_URL = "https://api.aviationstack.com/v1/flights"

# ============================================================
# STEP 6: LOAD AIRPORT INFORMATION
# ============================================================

# Load airport records indexed by their IATA codes.
# This allows the application to look up airport details using
# codes such as DAC, BLR, LHR, or JFK.

AIRPORTS = airportsdata.load("IATA")


# ============================================================
# STEP 7: DEFINE COUNTRY ALIASES
# ============================================================

# Map alternative country names, abbreviations, and common
# expressions to their standard ISO 3166-1 alpha-2 country codes.
#
# This helps the travel planner understand different ways users
# may mention a country in their travel requests.

COUNTRY_ALIASES = {
    # United States aliases
    "usa": "US",
    "u.s.a": "US",
    "u.s.": "US",
    "america": "US",
    "united states": "US",

    # United Kingdom aliases
    "uk": "GB",
    "u.k.": "GB",
    "britain": "GB",
    "england": "GB",

    # United Arab Emirates aliases
    "uae": "AE",
    "dubai": "AE",

    # South Korea aliases
    "south korea": "KR",
    "korea": "KR",

    # Other country names and their standard country codes
    "russia": "RU",
    "vietnam": "VN",
    "bangladesh": "BD",
    "india": "IN",
    "japan": "JP",
    "china": "CN",
    "singapore": "SG",
    "malaysia": "MY",
    "thailand": "TH",
    "indonesia": "ID",
    "nepal": "NP",
    "qatar": "QA",
    "saudi arabia": "SA",
    "turkey": "TR",
    "canada": "CA",
    "australia": "AU",
    "germany": "DE",
    "france": "FR",
    "italy": "IT",
    "spain": "ES",
}


# ============================================================
# STEP 8: MAP COUNTRIES TO THEIR DEFAULT AIRPORTS
# ============================================================

# Map each country's ISO country code to a representative
# airport's three-letter IATA code.
#
# These airports act as default destinations when the user
# provides a country name instead of a specific city or airport.
#
# IMPORTANT:
# A country can have multiple international airports.
# These are representative defaults, not necessarily the
# busiest or most suitable airports for every trip.

COUNTRY_MAIN_AIRPORT = {
    "BD": "DAC",  # Bangladesh        -> Hazrat Shahjalal International Airport, Dhaka
    "IN": "DEL",  # India             -> Indira Gandhi International Airport, Delhi
    "JP": "NRT",  # Japan             -> Narita International Airport, Tokyo area
    "US": "JFK",  # United States     -> John F. Kennedy International Airport, New York
    "GB": "LHR",  # United Kingdom    -> Heathrow Airport, London
    "AE": "DXB",  # United Arab Emirates -> Dubai International Airport
    "SG": "SIN",  # Singapore         -> Singapore Changi Airport
    "MY": "KUL",  # Malaysia          -> Kuala Lumpur International Airport
    "TH": "BKK",  # Thailand          -> Suvarnabhumi Airport, Bangkok
    "ID": "CGK",  # Indonesia         -> Soekarno-Hatta International Airport, Jakarta
    "CN": "PEK",  # China              -> Beijing Capital International Airport
    "KR": "ICN",  # South Korea       -> Incheon International Airport, Seoul area
    "NP": "KTM",  # Nepal             -> Tribhuvan International Airport, Kathmandu
    "QA": "DOH",  # Qatar             -> Hamad International Airport, Doha
    "SA": "JED",  # Saudi Arabia      -> King Abdulaziz International Airport, Jeddah
    "TR": "IST",  # Turkey             -> Istanbul Airport
    "CA": "YYZ",  # Canada            -> Toronto Pearson International Airport
    "AU": "SYD",  # Australia         -> Sydney Kingsford Smith Airport
    "DE": "FRA",  # Germany           -> Frankfurt Airport
    "FR": "CDG",  # France            -> Paris Charles de Gaulle Airport
    "IT": "FCO",  # Italy             -> Rome Fiumicino Airport
    "ES": "MAD",  # Spain             -> Adolfo Suárez Madrid-Barajas Airport
}



# ============================================================
# STEP 9: MAP CITY NAMES TO THEIR DEFAULT AIRPORTS
# ============================================================

# Map city names and alternative spellings to representative
# airport IATA codes.
#
# This helps the travel planner identify an airport when the
# user provides a city name instead of an airport code.
#
# Note:
# Some cities have multiple airports. These mappings select
# a default airport and may need adjustment for specific trips.

CITY_MAIN_AIRPORT = {
    # Bangladesh
    "dhaka": "DAC",             # Dhaka -> Hazrat Shahjalal International Airport

    # India
    "delhi": "DEL",             # Delhi -> Indira Gandhi International Airport
    "new delhi": "DEL",         # New Delhi -> Indira Gandhi International Airport
    "mumbai": "BOM",            # Mumbai -> Chhatrapati Shivaji Maharaj International Airport
    "kolkata": "CCU",            # Kolkata -> Netaji Subhas Chandra Bose International Airport
    "chennai": "MAA",            # Chennai -> Chennai International Airport
    "bangalore": "BLR",          # Bangalore -> Kempegowda International Airport
    "bengaluru": "BLR",          # Bengaluru -> Kempegowda International Airport

    # Japan
    "tokyo": "NRT",              # Tokyo -> Narita International Airport
    "osaka": "KIX",              # Osaka -> Kansai International Airport
    "kyoto": "KIX",              # Kyoto -> Kansai International Airport (default)

    # United States
    "new york": "JFK",           # New York -> John F. Kennedy International Airport

    # United Kingdom
    "london": "LHR",             # London -> Heathrow Airport

    # United Arab Emirates
    "dubai": "DXB",              # Dubai -> Dubai International Airport

    # Southeast Asia
    "singapore": "SIN",          # Singapore -> Singapore Changi Airport
    "kuala lumpur": "KUL",       # Kuala Lumpur -> Kuala Lumpur International Airport
    "bangkok": "BKK",            # Bangkok -> Suvarnabhumi Airport

    # Middle East
    "doha": "DOH",               # Doha -> Hamad International Airport

    # Turkey
    "istanbul": "IST",           # Istanbul -> Istanbul Airport

    # Canada
    "toronto": "YYZ",             # Toronto -> Toronto Pearson International Airport

    # Australia
    "sydney": "SYD",              # Sydney -> Sydney Kingsford Smith Airport

    # Europe
    "paris": "CDG",               # Paris -> Charles de Gaulle Airport
    "rome": "FCO",                # Rome -> Leonardo da Vinci–Fiumicino Airport
    "madrid": "MAD",              # Madrid -> Adolfo Suárez Madrid-Barajas Airport
    "frankfurt": "FRA",           # Frankfurt -> Frankfurt Airport
}

# ============================================================
# CLEAN AND NORMALIZE USER INPUT
# ============================================================
def clean_text(text: str) -> str:
    """
    Clean user input before extracting city, country, or airport names.

    Steps:
    1. Convert text to lowercase and remove surrounding spaces.
    2. Replace punctuation and special characters with spaces.
    3. Remove repeated spaces.
    4. Remove common travel-related words that do not identify a destination.
    5. Return the cleaned text.
    """

    # Step 1: Convert all letters to lowercase and remove spaces
    # from the beginning and end of the input.
    text = text.lower().strip()

    # Step 2: Replace characters other than English letters,
    # numbers, and whitespace with spaces.
    # Example: "Japan!" becomes "japan ".
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Step 3: Replace multiple consecutive whitespace characters
    # with a single space.
    # Example: "visit    japan" becomes "visit japan".
    text = re.sub(r"\s+", " ", text)

    # Step 4: Define common travel-related words that usually
    # do not help identify a destination.
    stop_words = [
        "flight", "flights", "ticket", "tickets", "trip", "travel",
        "plan", "complete", "days", "day", "including", "hotel",
        "hotels", "sightseeing", "under", "budget", "info", "information"
    ]

    # Step 5: Split the sentence into individual words and keep
    # only words that are not present in the stop_words list.
    words = [w for w in text.split() if w not in stop_words]

    # Step 6: Join the remaining words with single spaces and
    # remove any leftover spaces at the beginning or end.
    return " ".join(words).strip()


# ============================================================
# CONVERT COUNTRY NAMES INTO ISO COUNTRY CODES
# ============================================================

def country_name_to_code(text: str):
    """
    Identify a country in the given text and return its ISO
    alpha-2 country code.

    Examples:
        "India"                   -> "IN"
        "USA"                     -> "US"
        "Plan a trip to Japan"    -> "JP"
        "UnknownPlace"            -> None
    """

    # Step 1: Clean the input by converting it to lowercase,
    # removing punctuation, and filtering common travel words.
    text = clean_text(text)

    # Step 2: Check whether the entire cleaned text matches
    # a known country alias.
    # Example: "usa" -> "US", "india" -> "IN".
    if text in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[text]

    # Step 3: Ask pycountry to look up the country name or
    # recognized country identifier.
    # If a country is found, return its two-letter ISO code.
    try:
        country = pycountry.countries.lookup(text)
        return country.alpha_2

    # If pycountry cannot identify the country, continue
    # checking other possible matches.
    except LookupError:
        pass

    # Step 4: Check whether a full official country name
    # appears inside the longer input text.
    # Example: "travel to united states" contains "united states".
    for country in pycountry.countries:
        country_name = country.name.lower()

        if country_name in text:
            return country.alpha_2

    # Step 5: Check whether a known country alias appears
    # inside the input text.
    # Example: "trip to usa" contains the alias "usa".
    for alias, code in COUNTRY_ALIASES.items():
        if alias in text:
            return code

    # Step 6: Return None when no country can be identified.
    return None



# ============================================================
# CHECK WHETHER AN AIRPORT BELONGS TO A COUNTRY
# ============================================================

def airport_country_matches(airport: dict, country_code: str) -> bool:
    """
    Check whether an airport belongs to the requested country.

    Parameters:
        airport (dict): Dictionary containing airport information.
                        Example: {"name": "Kempegowda International Airport",
                                  "country": "IN"}

        country_code (str): Two-letter ISO country code.
                            Example: "IN" for India.

    Returns:
        bool: True if the airport belongs to the country,
              otherwise False.
    """

    # Step 1: Get the airport's country value.
    # If the "country" key is missing, use an empty string.
    # Convert the value to a string, uppercase it, and remove
    # unnecessary spaces.
    airport_country = str(
        airport.get("country", "")
    ).upper().strip()

    # Step 2: Compare the airport's country code with the
    # requested country code.
    # Example: "IN" == "IN" returns True.
    if airport_country == country_code:
        return True

    # Step 3: Handle cases where the airport's country is
    # stored as a full country name instead of a country code.
    try:
        # Look up the country using its two-letter ISO code.
        # Example: "IN" returns India's country information.
        country = pycountry.countries.get(
            alpha_2=country_code
        )

        # Step 4: If the country exists, compare its full name
        # with the airport's country value.
        # Example: "INDIA" == "india" returns True after
        # converting both values to lowercase.
        if country and airport_country.lower() == country.name.lower():
            return True

    # Step 5: If country lookup or comparison raises an
    # exception, ignore it and continue to the final result.
    except Exception:
        pass

    # Step 6: If neither comparison matches, the airport
    # does not match the requested country.
    return False


# ============================================================
# FIND THE BEST AIRPORT FOR A COUNTRY
# ============================================================
def get_best_airport_for_country(country_code: str):
    """
    Find a suitable airport for the given country.

    Parameters:
        country_code (str): Two-letter ISO country code.
                            Example: "IN" for India.

    Returns:
        str: IATA airport code, such as "DEL" or "JFK".
        None: If no matching airport is found.
    """
    preferred = COUNTRY_MAIN_AIRPORT.get(country_code)

    if preferred and preferred in AIRPORTS:
        return preferred

    candidates = []

    for iata, airport in AIRPORTS.items():
        if not iata:
            continue

        if airport_country_matches(airport, country_code):
            name = str(airport.get("name", "")).lower()
            city = str(airport.get("city", "")).lower()

            score = 0

            if "international" in name:
                score += 50
            if "intl" in name:
                score += 40
            if "capital" in name:
                score += 20
            if city:
                score += 5

            candidates.append((score, iata))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    return candidates[0][1]

# ============================================================
# CONVERT A LOCATION INTO AN IATA AIRPORT CODE
# ============================================================
def resolve_location_to_iata(location: str):
    """
    Convert a country, city, airport name, or IATA code
    into an airport's three-letter IATA code.

    Examples:
        Bangladesh -> DAC
        Japan      -> NRT
        Dhaka      -> DAC
        Tokyo      -> NRT
        DAC        -> DAC

    Returns:
        str: The resolved airport code, such as "DAC".
        None: If the location cannot be resolved.
    """

    if not location:
        return None

    raw_location = location.strip()

    # Direct IATA code
    if re.fullmatch(r"[A-Za-z]{3}", raw_location):
        code = raw_location.upper()
        if code in AIRPORTS:
            return code

    location_clean = clean_text(raw_location)

    if not location_clean:
        return None

    # City preferred airport
    if location_clean in CITY_MAIN_AIRPORT:
        return CITY_MAIN_AIRPORT[location_clean]

    # Country preferred airport
    country_code = country_name_to_code(location_clean)
    if country_code:
        airport = get_best_airport_for_country(country_code)
        if airport:
            return airport

    # Exact city match from airport database
    city_matches = []

    for iata, airport in AIRPORTS.items():
        city = str(airport.get("city", "")).lower().strip()
        name = str(airport.get("name", "")).lower().strip()

        score = 0

        if city == location_clean:
            score += 100
        elif location_clean in city:
            score += 70

        if location_clean in name:
            score += 50

        if "international" in name:
            score += 10

        if score > 0:
            city_matches.append((score, iata))

    if city_matches:
        city_matches.sort(reverse=True)
        return city_matches[0][1]

    return None

# ============================================================
# FIND CITY AND COUNTRY NAMES IN A USER QUERY
# ============================================================
def find_location_mentions(query: str):
    """
    Find country aliases, official country names, and city names
    mentioned in a natural-language query.

    Parameters:
        query (str): The complete sentence entered by the user.

    Returns:
        list: Unique location mentions in the order they
              were discovered.
    """

    q = query.lower()
    mentions = []

    # Country aliases
    for alias in COUNTRY_ALIASES:
        if re.search(rf"\b{re.escape(alias)}\b", q):
            mentions.append(alias)

    # Country names from pycountry
    for country in pycountry.countries:
        name = country.name.lower()
        if len(name) >= 4 and re.search(rf"\b{re.escape(name)}\b", q):
            mentions.append(name)

    # City names from our preferred city map
    for city in CITY_MAIN_AIRPORT:
        if re.search(rf"\b{re.escape(city)}\b", q):
            mentions.append(city)

    # Remove duplicate while keeping order
    unique_mentions = []
    for item in mentions:
        if item not in unique_mentions:
            unique_mentions.append(item)

    return unique_mentions

# ============================================================
# PARSE THE USER'S FLIGHT ROUTE
# ============================================================

def parse_route(query: str):
    """
    Extract departure and arrival airport codes from a
    natural-language flight query.

    Examples:
        "Flights from Dhaka to Tokyo" -> ("DAC", "NRT")
        "Flights from Bengaluru"      -> ("BLR", None)
        "Flights to Japan"            -> (None, "NRT")
        "Show all global flights"     -> (None, None)

    Returns:
        tuple: (departure_iata, arrival_iata)
    """

    q = query.strip()
    q_lower = q.lower()

    # Global / all-country query
    global_keywords = [
        "all country",
        "all countries",
        "global flight",
        "global flights",
        "all flight",
        "all flights",
        "worldwide flight",
        "worldwide flights",
    ]

    if any(keyword in q_lower for keyword in global_keywords):
        return None, None

    # Direct IATA code route: DAC to NRT
    codes = re.findall(r"\b[A-Z]{3}\b", q)

    if len(codes) >= 2:
        dep = codes[0].upper()
        arr = codes[1].upper()
        return dep, arr

    # Pattern: from X to Y
    match = re.search(
        r"\bfrom\s+(.+?)\s+\bto\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        origin_text = match.group(1)
        dest_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: to Y from X
    match = re.search(
        r"\bto\s+(.+?)\s+\bfrom\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        dest_text = match.group(1)
        origin_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: flights from X
    match = re.search(r"\bfrom\s+(.+?)(?:[.!?]|$)", q_lower)

    if match:
        origin_text = match.group(1)
        dep_iata = resolve_location_to_iata(origin_text)
        return dep_iata, None

    # Pattern: flights to X
    match = re.search(r"\bto\s+(.+?)(?:[.!?]|$)", q_lower)

    if match:
        dest_text = match.group(1)
        arr_iata = resolve_location_to_iata(dest_text)
        return None, arr_iata

    # Fallback: find country/city mentions
    mentions = find_location_mentions(q)

    if len(mentions) >= 2:
        dep_iata = resolve_location_to_iata(mentions[0])
        arr_iata = resolve_location_to_iata(mentions[1])
        return dep_iata, arr_iata

    if len(mentions) == 1:
        arr_iata = resolve_location_to_iata(mentions[0])
        return DEFAULT_ORIGIN_IATA, arr_iata

    return None, None

# ============================================================
# FORMAT FLIGHT DETAILS INTO READABLE TEXT
# ============================================================

def format_flight(flight: dict):
    """
    Convert a flight record into human-readable text.

    Parameters:
        flight (dict): A dictionary containing flight details
                       returned by the Aviationstack API.

    Returns:
        str: A formatted summary of the flight.
    """
    airline = flight.get("airline", {}).get("name") or "Unknown airline"
    flight_number = flight.get("flight", {}).get("iata") or "Unknown flight number"
    status = flight.get("flight_status") or "Unknown"

    dep = flight.get("departure", {}) or {}
    arr = flight.get("arrival", {}) or {}

    dep_airport = dep.get("airport") or "Unknown departure airport"
    dep_iata = dep.get("iata") or "Unknown"
    dep_terminal = dep.get("terminal") or "N/A"
    dep_gate = dep.get("gate") or "N/A"
    dep_scheduled = dep.get("scheduled") or "Unknown"
    dep_delay = dep.get("delay")
    dep_delay_text = f"{dep_delay} minutes" if dep_delay is not None else "N/A"

    arr_airport = arr.get("airport") or "Unknown arrival airport"
    arr_iata = arr.get("iata") or "Unknown"
    arr_terminal = arr.get("terminal") or "N/A"
    arr_gate = arr.get("gate") or "N/A"
    arr_scheduled = arr.get("scheduled") or "Unknown"
    arr_delay = arr.get("delay")
    arr_delay_text = f"{arr_delay} minutes" if arr_delay is not None else "N/A"

    return f"""
        Airline: {airline}
        Flight: {flight_number}
        Status: {status}

        Departure:
        - Airport: {dep_airport}
        - IATA: {dep_iata}
        - Terminal: {dep_terminal}
        - Gate: {dep_gate}
        - Scheduled: {dep_scheduled}
        - Delay: {dep_delay_text}

        Arrival:
        - Airport: {arr_airport}
        - IATA: {arr_iata}
        - Terminal: {arr_terminal}
        - Gate: {arr_gate}
        - Scheduled: {arr_scheduled}
        - Delay: {arr_delay_text}
        """.strip()

# ============================================================
# SEARCH FLIGHTS USING THE AVIATIONSTACK API
# ============================================================

def search_flights(query: str, limit: int = 10):
    """
    Search for flight information using the Aviationstack API.

    Parameters:
        query (str): The user's natural-language flight query.
                     Example: "Flights from Bengaluru to Tokyo"

        limit (int): Maximum number of flight records to request.
                     Default is 10; the API request is capped at 100.

    Returns:
        str: Formatted flight information or an error message.
    """

    if not API_KEY:
        return (
            "Flight API error: AVIATIONSTACK_API_KEY is missing.\n"
            "Please add this in your .env file:\n"
            "AVIATIONSTACK_API_KEY=your_api_key_here"
        )

    dep_iata, arr_iata = parse_route(query)

    params = {
        "access_key": API_KEY,
        "limit": min(limit, 100),
    }

    if dep_iata:
        params["dep_iata"] = dep_iata

    if arr_iata:
        params["arr_iata"] = arr_iata

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Flight API request failed: {e}"
    except ValueError:
        return "Flight API returned invalid JSON."

    if "error" in data:
        error = data["error"]
        return (
            "Flight API error:\n"
            f"Code: {error.get('code', 'Unknown')}\n"
            f"Message: {error.get('message', 'Unknown error')}"
        )

    flight_data = data.get("data", [])

    if not flight_data:
        route_text = ""

        if dep_iata and arr_iata:
            route_text = f" for route {dep_iata} to {arr_iata}"
        elif dep_iata:
            route_text = f" from {dep_iata}"
        elif arr_iata:
            route_text = f" to {arr_iata}"

        return (
            f"No live flight data found{route_text}.\n\n"
            "Note: AviationStack provides live/status flight data, not ticket prices. "
            "For actual fare prices, use a flight-pricing API such as Amadeus."
        )

    route_info = "Global live flights"

    if dep_iata and arr_iata:
        route_info = f"Live flights from {dep_iata} to {arr_iata}"
    elif dep_iata:
        route_info = f"Live flights from {dep_iata}"
    elif arr_iata:
        route_info = f"Live flights to {arr_iata}"

    formatted_flights = [format_flight(flight) for flight in flight_data[:limit]]

    return f"{route_info}\n\n" + "\n\n---\n\n".join(formatted_flights)


if __name__ == "__main__":
    print(search_flights("Plan a 7 days Japan trip from Bangladesh"))
    print("\n" + "=" * 80 + "\n")
    print(search_flights("all country flight info"))