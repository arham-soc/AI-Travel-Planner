import streamlit as st
import json
import os
from serpapi import GoogleSearch 
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
from agno.models.google import Gemini
from datetime import datetime, timedelta
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# Set up Streamlit UI 
st.set_page_config(
    page_title="🌍 AI Travel Planner", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styles
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #4b5563;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e40af;
        margin: 1.5rem 0 1rem 0;
        border-left: 4px solid #1e40af;
        padding-left: 1rem;
        background: #f0f9ff;
        padding: 1rem;
        border-radius: 8px;
    }
    .flight-card {
        border: 2px solid #d1d5db;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .flight-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .success-banner {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        border: 2px solid #047857;
    }
    .info-box {
        background: #dbeafe;
        border-left: 4px solid #2563eb;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #1e3a8a;
        font-weight: 500;
    }
    .sidebar-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    .progress-bar {
        height: 8px;
        background: linear-gradient(90deg, #059669, #10b981);
        border-radius: 4px;
        margin: 1rem 0;
    }
    .booking-button {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
        text-decoration: none;
        display: block;
        text-align: center;
        transition: all 0.3s ease;
    }
    .booking-button:hover {
        background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
    }
    .theme-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        text-align: center;
        border: 2px solid #4f46e5;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and subtitle
st.markdown('<h1 class="main-title">✈️ Travel Planner </h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your intelligent travel companion for personalized trip planning</p>', unsafe_allow_html=True)

# Airport data 
airport_list = sorted([
    # 🇵🇰 Pakistan
    "ISB - Islamabad (Pakistan)",
    "KHI - Karachi (Pakistan)",
    "LHE - Lahore (Pakistan)",
    "MUX - Multan (Pakistan)",
    "PEW - Peshawar (Pakistan)",
    "SKT - Sialkot (Pakistan)",
    "UET - Quetta (Pakistan)",
    "RYK - Rahim Yar Khan (Pakistan)",
    "GWD - Gwadar (Pakistan)",
    "LYP - Faisalabad (Pakistan)",
    "TUK - Turbat (Pakistan)",

    # 🇮🇳 India
    "DEL - Delhi (India)",
    "BOM - Mumbai (India)",
    "BLR - Bengaluru (India)",
    "MAA - Chennai (India)",
    "HYD - Hyderabad (India)",
    "CCU - Kolkata (India)",
    "GOI - Goa (India)",
    "AMD - Ahmedabad (India)",
    "PNQ - Pune (India)",
    "COK - Kochi (India)",
    "TRV - Thiruvananthapuram (India)",
    "JAI - Jaipur (India)",
    "VNS - Varanasi (India)",
    "LKO - Lucknow (India)",
    "PAT - Patna (India)",
    "IXC - Chandigarh (India)",
    "BBI - Bhubaneswar (India)",
    "GAU - Guwahati (India)",

    # 🇦🇪 United Arab Emirates
    "DXB - Dubai (UAE)",
    "AUH - Abu Dhabi (UAE)",
    "SHJ - Sharjah (UAE)",
    "DWC - Dubai World Central (UAE)",
    "RKT - Ras Al Khaimah (UAE)",
    "FJR - Fujairah (UAE)",

    # 🇸🇦 Saudi Arabia
    "JED - Jeddah (Saudi Arabia)",
    "RUH - Riyadh (Saudi Arabia)",
    "MED - Madinah (Saudi Arabia)",
    "DMM - Dammam (Saudi Arabia)",
    "TIF - Taif (Saudi Arabia)",
    "YNB - Yanbu (Saudi Arabia)",

    # 🇴🇲 Oman
    "MCT - Muscat (Oman)",
    "SLL - Salalah (Oman)",

    # 🇶🇦 Qatar
    "DOH - Doha (Qatar)",

    # 🇧🇭 Bahrain
    "BAH - Manama (Bahrain)",

    # 🇰🇼 Kuwait
    "KWI - Kuwait City (Kuwait)",

    # 🇹🇷 Turkey
    "IST - Istanbul (Turkey)",
    "SAW - Sabiha Gokcen (Turkey)",
    "ESB - Ankara (Turkey)",
    "ADB - Izmir (Turkey)",

    # 🇪🇬 Egypt
    "CAI - Cairo (Egypt)",
    "HRG - Hurghada (Egypt)",
    "SSH - Sharm El Sheikh (Egypt)",

    # 🇬🇧 United Kingdom
    "LHR - London Heathrow (UK)",
    "LGW - London Gatwick (UK)",
    "MAN - Manchester (UK)",
    "EDI - Edinburgh (UK)",
    "BHX - Birmingham (UK)",
    "BRS - Bristol (UK)",
    "GLA - Glasgow (UK)",

    # 🇩🇪 Germany
    "FRA - Frankfurt (Germany)",
    "MUC - Munich (Germany)",
    "BER - Berlin (Germany)",
    "DUS - Düsseldorf (Germany)",
    "HAM - Hamburg (Germany)",

    # 🇫🇷 France
    "CDG - Paris Charles de Gaulle (France)",
    "ORY - Paris Orly (France)",
    "LYS - Lyon (France)",
    "NCE - Nice (France)",

    # 🇪🇸 Spain
    "MAD - Madrid (Spain)",
    "BCN - Barcelona (Spain)",
    "AGP - Malaga (Spain)",
    "PMI - Palma de Mallorca (Spain)",

    # 🇮🇹 Italy
    "FCO - Rome Fiumicino (Italy)",
    "MXP - Milan Malpensa (Italy)",
    "VCE - Venice (Italy)",
    "NAP - Naples (Italy)",

    # 🇳🇱 Netherlands
    "AMS - Amsterdam (Netherlands)",

    # 🇨🇭 Switzerland
    "ZRH - Zurich (Switzerland)",
    "GVA - Geneva (Switzerland)",

    # 🇸🇬 Singapore
    "SIN - Singapore (Singapore)",

    # 🇹🇭 Thailand
    "BKK - Bangkok (Thailand)",
    "HKT - Phuket (Thailand)",
    "CNX - Chiang Mai (Thailand)",

    # 🇲🇾 Malaysia
    "KUL - Kuala Lumpur (Malaysia)",
    "PEN - Penang (Malaysia)",
    "LGK - Langkawi (Malaysia)",

    # 🇨🇳 China
    "PEK - Beijing (China)",
    "PVG - Shanghai (China)",
    "CAN - Guangzhou (China)",
    "HKG - Hong Kong (China)",

    # 🇯🇵 Japan
    "NRT - Tokyo Narita (Japan)",
    "HND - Tokyo Haneda (Japan)",
    "KIX - Osaka (Japan)",

    # 🇺🇸 United States
    "JFK - New York (USA)",
    "LAX - Los Angeles (USA)",
    "ORD - Chicago O'Hare (USA)",
    "SFO - San Francisco (USA)",
    "DFW - Dallas Fort Worth (USA)",
    "MIA - Miami (USA)",
    "SEA - Seattle (USA)",
    "BOS - Boston (USA)",
    "ATL - Atlanta (USA)",
    "LAS - Las Vegas (USA)",

    # 🇨🇦 Canada
    "YYZ - Toronto (Canada)",
    "YVR - Vancouver (Canada)",
    "YUL - Montreal (Canada)",
    "YYC - Calgary (Canada)",

    # 🇦🇺 Australia
    "SYD - Sydney (Australia)",
    "MEL - Melbourne (Australia)",
    "BNE - Brisbane (Australia)",
    "PER - Perth (Australia)",

    # 🌎 Others (popular global hubs)
    "GRU - São Paulo (Brazil)",
    "EZE - Buenos Aires (Argentina)",
    "JNB - Johannesburg (South Africa)",
])

# Currency mapping function
def get_local_currency(departure_city):
    """Get local currency based on departure city"""
    currency_map = {
        # Pakistan
        "KHI": ("PKR", "₨"), "ISB": ("PKR", "₨"), "LHE": ("PKR", "₨"),
        "MUX": ("PKR", "₨"), "PEW": ("PKR", "₨"), "SKT": ("PKR", "₨"),
        
        # India
        "DEL": ("INR", "₹"), "BOM": ("INR", "₹"), "BLR": ("INR", "₹"),
        "MAA": ("INR", "₹"), "HYD": ("INR", "₹"), "CCU": ("INR", "₹"),
        
        # UAE
        "DXB": ("AED", "د.إ"), "AUH": ("AED", "د.إ"), "SHJ": ("AED", "د.إ"),
        
        # Saudi Arabia
        "JED": ("SAR", "﷼"), "RUH": ("SAR", "﷼"), "MED": ("SAR", "﷼"),
        
        # Other countries
        "LHR": ("GBP", "£"), "LGW": ("GBP", "£"),  # UK
        "JFK": ("USD", "$"), "LAX": ("USD", "$"),   # USA
        "SIN": ("SGD", "S$"),                       # Singapore
        "BKK": ("THB", "฿"),                        # Thailand
        "KUL": ("MYR", "RM"),                       # Malaysia
    }
    
    # Default to USD if not found
    return currency_map.get(departure_city, ("USD", "$"))

def convert_currency(amount_usd, target_currency):
    """Convert USD to local currency (simplified rates)"""
    conversion_rates = {
        "PKR": 280,    # 1 USD = 280 PKR
        "INR": 83,     # 1 USD = 83 INR
        "AED": 3.67,   # 1 USD = 3.67 AED
        "SAR": 3.75,   # 1 USD = 3.75 SAR
        "GBP": 0.79,   # 1 USD = 0.79 GBP
        "EUR": 0.92,   # 1 USD = 0.92 EUR
        "SGD": 1.35,   # 1 USD = 1.35 SGD
        "THB": 36.5,   # 1 USD = 36.5 THB
        "MYR": 4.75,   # 1 USD = 4.75 MYR
    }
    
    rate = conversion_rates.get(target_currency, 1)
    local_amount = amount_usd * rate
    return round(local_amount, 2)

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem; padding: 1rem; background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); border-radius: 10px; color: white;'>
            <h2>🌎 Travel Assistant</h2>
            <p>Personalize your journey</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Travel Preferences in cards
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("🎯 Travel Preferences")
    budget = st.radio("💰 Budget Preference:", ["Economy", "Standard", "Luxury"], horizontal=True)
    flight_class = st.radio("✈️ Flight Class:", ["Economy", "Premium Economy", "Business", "First"], horizontal=True)
    hotel_rating = st.selectbox("🏨 Hotel Rating:", ["Any", "3⭐ & above", "4⭐ & above", "5⭐ Only"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Packing Checklist
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("🎒 Packing Checklist")
    
    packing_items = {
        "👕 Clothes": True,
        "👟 Comfortable Footwear": True, 
        "🕶️ Sunglasses & Sunscreen": False,
        "📱 Electronics & Chargers": False,
        "💊 Medications & First-Aid": True,
        "📄 Travel Documents": True,
        "💳 Money & Cards": True,
        "🧴 Toiletries": False
    }
    
    for item, default in packing_items.items():
        st.checkbox(item, value=default, key=f"pack_{item}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Travel Essentials
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.subheader("🛂 Travel Essentials")
    visa_required = st.checkbox("🛃 Check Visa Requirements", value=True)
    travel_insurance = st.checkbox("🛡️ Get Travel Insurance", value=True)
    currency_info = st.checkbox("💱 Currency Exchange Info", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="section-header">📍 Trip Details</div>', unsafe_allow_html=True)
    
    # Departure and Destination
    col1a, col1b = st.columns(2)
    with col1a:
        source_full = st.selectbox("🛫 Departure City:", airport_list, key="departure")
        source = source_full.split(" - ")[0]
    with col1b:
        destination_full = st.selectbox("🛬 Destination:", airport_list, key="destination") 
        destination = destination_full.split(" - ")[0]
    
    # Trip Duration with visual slider
    st.markdown("**🕒 Trip Duration**")
    num_days = st.slider("Select number of days", 1, 30, 7, label_visibility="collapsed")
    st.progress(min(num_days / 30, 1.0))
    st.caption(f"🎯 {num_days} day{'s' if num_days > 1 else ''} selected")
    
    # Travel Theme with icons
    travel_theme = st.selectbox(
        "🎭 Travel Theme:",
        ["💑 Romantic Getaway", "👨‍👩‍👧‍👦 Family Vacation", "🏔️ Adventure Trip", 
         "🧳 Solo Exploration", "💼 Business Trip", "🎓 Educational Tour"]
    )

with col2:
    st.markdown('<div class="section-header">📅 Travel Dates</div>', unsafe_allow_html=True)
    
    # Date inputs 
    today = datetime.today()
    departure_date = st.date_input(
        "📅 Departure Date", 
        min_value=today,
        value=today + timedelta(days=7)
    )
    return_date = st.date_input(
        "📅 Return Date",
        min_value=departure_date,
        value=departure_date + timedelta(days=num_days)
    )
    
    # Date validation
    if return_date <= departure_date:
        st.error("⚠️ Return date must be after departure date")
    
    # Trip summary
    st.markdown("""
        <div style='background: #dbeafe; padding: 1.5rem; border-radius: 10px; margin-top: 1rem; border: 1px solid #93c5fd;'>
            <h4 style='color: #1e3a8a; margin-bottom: 1rem;'>📊 Trip Summary</h4>
            <p style='color: #374151;'><strong>Duration:</strong> {} days</p>
            <p style='color: #374151;'><strong>Budget:</strong> {}</p>
            <p style='color: #374151;'><strong>Class:</strong> {}</p>
        </div>
    """.format(num_days, budget, flight_class), unsafe_allow_html=True)

# Activity Preferences with enhanced input
st.markdown('<div class="section-header">🌍 Travel Preferences</div>', unsafe_allow_html=True)

activity_preferences = st.text_area(
    "**What kind of experiences are you looking for?** \n*(e.g. historical sites, adventure sports, culinary experiences, shopping, nightlife, cultural immersion, etc.)*",
    "Exploring historical sites and local cuisine",
    height=80
)

# Smart activity detection 
if activity_preferences:
    pref = activity_preferences.lower()
    activity_icons = {
        "business": ("💼", "Business trip detected! We'll focus on convenient locations and meeting venues."),
        "beach": ("🏖️", "Beach vacation! Let's find the best coastal destinations and water activities."),
        "adventure": ("🧗", "Adventure mode activated! Expect thrilling outdoor experiences."),
        "nightlife": ("🌃", "Nightlife enthusiast! We'll include vibrant clubs and evening entertainment."),
        "romantic": ("💞", "Romantic getaway! Planning cozy and intimate experiences."),
        "shopping": ("🛍️", "Shopping spree ahead! Mapping out the best markets and malls."),
        "family": ("👨‍👩‍👧‍👦", "Family vacation! Focusing on kid-friendly and safe destinations."),
        "solo": ("🚶", "Solo adventure! Curating independent travel experiences."),
        "culture": ("🏛️", "Cultural exploration! Including museums, landmarks, and local traditions.")
    }
    
    detected_activity = None
    for key, (icon, message) in activity_icons.items():
        if key in pref:
            detected_activity = (icon, message)
            break
    
    if detected_activity:
        st.markdown(f"""
            <div class="info-box">
                <h4 style='color: #1e3a8a; margin: 0;'>{detected_activity[0]} {detected_activity[1]}</h4>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="info-box">
                <h4 style='color: #1e3a8a; margin: 0;'>✨ Great! We'll tailor your trip around: {activity_preferences}</h4>
            </div>
        """, unsafe_allow_html=True)

# Theme Banner with colors
st.markdown(f"""
    <div class="theme-banner">
        <h3>🌟 Your {travel_theme} to {destination_full} is about to begin! 🌟</h3>
        <p>Let's find the best flights, stays, and experiences for your unforgettable journey.</p>
    </div>
""", unsafe_allow_html=True)

# API Keys
#SERPAPI_KEY = "a82c62745f2b9141591f5e90ecc937fe23044f81da364ecf0719446438682d84"
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Helper functions
def format_datetime(iso_string):
    try:
        dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
        return dt.strftime("%b %d, %Y | %I:%M %p")
    except:
        return "Time not specified"

def fetch_flights(source, destination, departure_date, return_date):
    """Fetch flight data from SerpAPI"""
    try:
        params = {
            "engine": "google_flights",
            "departure_id": source,
            "arrival_id": destination,
            "outbound_date": str(departure_date),
            "return_date": str(return_date),
            "currency": "USD",
            "hl": "en",
            "api_key": SERPAPI_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        return results
    except Exception as e:
        st.error(f"Error fetching flights: {str(e)}")
        return None

def extract_cheapest_flights(flight_data):
    """Extract top 3 cheapest flights"""
    if not flight_data:
        return []
    
    best_flights = flight_data.get("best_flights", [])
    sorted_flights = sorted(best_flights, key=lambda x: x.get("price", float("inf")))[:3]
    return sorted_flights

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# AI Agent - Researcher
researcher = Agent(
    name="Researcher",
    instructions=[
        f"Current date and time is {current_time}.",
        "Identify the travel destination specified by the user.",
        "Gather detailed information on the destination, including climate, culture, and safety tips.",
        "Find popular attractions, landmarks, and must-visit places.",
        "Search for activities that match the user's interests and travel style.",
        "Prioritize information from reliable sources and official travel guides.",
        "Provide well-structured summaries with key insights and recommendations.",
        "Include practical information like best times to visit, local customs, and transportation options."
    ],
    model=Gemini(id="gemini-2.0-flash-exp", api_key=GOOGLE_API_KEY),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
)

# AI Agent - Planner
planner = Agent(
    name="Planner",
    instructions=[
        f"Current date and time is {current_time}.",
        "Gather details about the user's travel preferences and budget.",
        "Create a detailed itinerary with scheduled activities and estimated costs.",
        "Ensure the itinerary includes transportation options and travel time estimates.",
        "Optimize the schedule for convenience and enjoyment.",
        "Present the itinerary in a structured format with clear day-by-day breakdown.",
        "Include time buffers between activities and realistic travel times.",
        "Provide cost estimates for activities, meals, and transportation.",
        "Consider the travel theme and preferences in activity selection."
    ],
    model=Gemini(id="gemini-2.0-flash-exp", api_key=GOOGLE_API_KEY),
)

# AI Agent - Hotel & Restaurant Finder
hotel_restaurant_finder = Agent(
    name="Hotel & Restaurant Finder",
    instructions=[
        f"Current date and time is {current_time}.",
        "Identify key locations in the user's travel itinerary.",
        "Search for highly rated hotels near those locations.",
        "Search for top-rated restaurants based on cuisine preferences and proximity.",
        "Prioritize results based on user preferences, ratings, and availability.",
        "Provide specific recommendations with prices, ratings, and unique features.",
        "Include both budget and luxury options based on user preference.",
        "Consider dietary preferences and special requirements.",
        "Provide direct booking links or reservation options where possible."
    ],
    model=Gemini(id="gemini-2.0-flash-exp", api_key=GOOGLE_API_KEY),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
)

# Generate Travel Plan Button
st.markdown("---")
generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
with generate_col2:
    generate_clicked = st.button(
        "🚀 Generate My Travel Plan", 
        use_container_width=True,
        type="primary",
        help="Click to create your personalized travel itinerary"
    )

if generate_clicked:
    if not all([source, destination, departure_date, return_date]):
        st.error("❌ Please fill in all required fields")
        st.stop()
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Fetch Flights
    status_text.text("✈️ Searching for the best flight options...")
    flight_data = fetch_flights(source, destination, departure_date, return_date)
    cheapest_flights = extract_cheapest_flights(flight_data)
    progress_bar.progress(25)
    time.sleep(1)
    
    # Step 2: Research Activities
    status_text.text("🔍 Researching attractions and activities...")
    research_prompt = f"""
    Research {destination} for a {num_days}-day {travel_theme.lower()} trip. 
    Traveler interests: {activity_preferences}. Budget: {budget}. 
    Focus on: popular attractions, local culture, safety tips, and unique experiences.
    Provide structured recommendations.
    """
    research_results = researcher.run(research_prompt, stream=False)
    progress_bar.progress(50)
    time.sleep(1)
    
    # Step 3: Find Hotels & Restaurants
    status_text.text("🏨 Finding accommodations and dining options...")
    hotel_prompt = f"""
    Find hotels and restaurants in {destination} for {travel_theme.lower()}.
    Budget: {budget}. Hotel preference: {hotel_rating}.
    Activities: {activity_preferences}. Provide specific recommendations with ratings and prices.
    """
    hotel_restaurant_results = hotel_restaurant_finder.run(hotel_prompt, stream=False)
    progress_bar.progress(75)
    time.sleep(1)
    
    # Step 4: Create Itinerary
    status_text.text("🗓️ Creating your personalized itinerary...")
    itinerary_prompt = f"""
    Create a detailed {num_days}-day itinerary for {destination}.
    Theme: {travel_theme}. Budget: {budget}. Interests: {activity_preferences}.
    Include: daily schedules, transportation, costs, and practical tips.
    Make it realistic with proper time allocation between activities.
    Research data: {research_results.content}
    Hotels & restaurants: {hotel_restaurant_results.content}
    """
    itinerary = planner.run(itinerary_prompt, stream=False)
    progress_bar.progress(100)
    status_text.text("✅ Travel plan completed!")
    
    time.sleep(1)
    progress_bar.empty()
    status_text.empty()
    
    # Display Results
    st.balloons()

    # Flights Section with local currency 
    st.markdown('<div class="section-header">✈️ Best Flight Options</div>', unsafe_allow_html=True)

    if cheapest_flights:
        cols = st.columns(len(cheapest_flights))

        def format_duration(minutes):
            """Convert minutes to hours and minutes format"""
            try:
                minutes = int(minutes)
                hours = minutes // 60
                mins = minutes % 60
                
                if hours > 0 and mins > 0:
                    return f"{hours}h {mins}m"
                elif hours > 0:
                    return f"{hours}h"
                else:
                    return f"{mins}m"
            except:
                return "N/A"
        
        for idx, flight in enumerate(cheapest_flights):
            with cols[idx]:
                # Get airline name properly
                flights_info = flight.get("flights", [{}])
                airline_info = flights_info[0].get("airline", "Unknown Airline") if flights_info else "Unknown Airline"
                airline_name = airline_info if airline_info != "Unknown Airline" else "Available Airline"
                
                price_usd = flight.get("price", 0)
                
                # Get local currency based on departure city
                local_currency_code, local_currency_symbol = get_local_currency(source)
                local_price = convert_currency(price_usd, local_currency_code)
                
                duration = flight.get("total_duration", "N/A")
                formatted_duration = format_duration(duration)
                
                # Flight details
                departure_info = flights_info[0].get("departure_airport", {})
                arrival_info = flights_info[-1].get("arrival_airport", {})
                
                departure_time = format_datetime(departure_info.get("time", "N/A"))
                arrival_time = format_datetime(arrival_info.get("time", "N/A"))
                
                # Generate Flights booking link with CURRENCY PARAMETER
                google_currency_codes = {
                    "PKR": "PKR", "INR": "INR", "AED": "AED", "SAR": "SAR",
                    "GBP": "GBP", "USD": "USD", "EUR": "EUR"
                }
                currency_param = google_currency_codes.get(local_currency_code, "USD")
                
                booking_link = f"https://www.google.com/travel/flights?q=Flights%20to%20{destination}%20from%20{source}&currency={currency_param}"
                
                # Create flight card 
                flight_card_html = (
                    '<div class="flight-card">'
                    '<div style="text-align: center;">'
                    f'<h3 style="color: #1e3a8a; margin-bottom: 1rem;">✈️ {airline_name}</h3>'
                    f'<div style="font-size: 1.8rem; font-weight: bold; color: #dc2626; margin: 1rem 0;">'
                    f'{local_currency_symbol}{local_price:,} {local_currency_code}'
                    '</div>'
                    '<div style="margin: 1rem 0; color: #374151;">'
                    f'<p><strong>🛫 Departure:</strong> {departure_time}</p>'
                    f'<p><strong>🛬 Arrival:</strong> {arrival_time}</p>'
                    f'<p><strong>⏱️ Duration:</strong> {formatted_duration} mins</p>'
                    f'<p><strong>🎫 Class:</strong> {flight_class}</p>'
                    '</div>'
                    f'<a href="{booking_link}" target="_blank" class="booking-button">'
                    '🎫 Book Now'
                    '</a>'
                    '</div>'
                    '</div>'
                )
                
                st.markdown(flight_card_html, unsafe_allow_html=True)
    else:
        st.warning("No flight data available. Showing demo flights.")
        # Demo flight cards with booking links and LOCAL CURRENCY ONLY
        demo_cols = st.columns(3)
        demo_flights = [
            {"airline": "Emirates", "price": 450, "duration": "4h 30m", "stops": "Non-stop"},
            {"airline": "Qatar Airways", "price": 520, "duration": "5h 15m", "stops": "1 Stop"}, 
            {"airline": "Turkish Airlines", "price": 480, "duration": "6h 0m", "stops": "Non-stop"}
        ]
        
        for idx, flight in enumerate(demo_flights):
            with demo_cols[idx]:
                # Get local currency for demo flights
                local_currency_code, local_currency_symbol = get_local_currency(source)
                local_price = convert_currency(flight['price'], local_currency_code)
                
                # Google Flights link with currency parameter
                google_currency_codes = {
                    "PKR": "PKR", "INR": "INR", "AED": "AED", "SAR": "SAR",
                    "GBP": "GBP", "USD": "USD", "EUR": "EUR"
                }
                currency_param = google_currency_codes.get(local_currency_code, "USD")
                
                booking_link = f"https://www.google.com/travel/flights?q={flight['airline']}%20Flights%20to%20{destination}%20from%20{source}&currency={currency_param}"
                
                # Demo card 
                demo_card_html = (
                    '<div class="flight-card">'
                    '<div style="text-align: center;">'
                    f'<h3 style="color: #1e3a8a; margin-bottom: 1rem;">✈️ {flight["airline"]}</h3>'
                    f'<div style="font-size: 1.8rem; font-weight: bold; color: #dc2626; margin: 1rem 0;">'
                    f'{local_currency_symbol}{local_price:,} {local_currency_code}'
                    '</div>'
                    '<div style="margin: 1rem 0; color: #374151;">'
                    f'<p><strong>⏱️ Duration:</strong> {flight["duration"]}</p>'
                    f'<p><strong>🛑 Stops:</strong> {flight["stops"]}</p>'
                    f'<p><strong>🎫 Class:</strong> {flight_class}</p>'
                    '</div>'
                    f'<a href="{booking_link}" target="_blank" class="booking-button">'
                    '🎫 Book Now'
                    '</a>'
                    '</div>'
                    '</div>'
                )
                
                st.markdown(demo_card_html, unsafe_allow_html=True)
    
    # Hotels & Restaurants Section
    st.markdown('<div class="section-header">🏨 Accommodation & Dining</div>', unsafe_allow_html=True)
    
    # Enhanced display for hotels and restaurants
    hotel_col, restaurant_col = st.columns(2)
    
    with hotel_col:
        st.subheader("🏨 Recommended Hotels")
        st.info(hotel_restaurant_results.content.split('Restaurants:')[0] if 'Restaurants:' in hotel_restaurant_results.content else hotel_restaurant_results.content)
    
    with restaurant_col:
        st.subheader("🍽️ Dining Options") 
        restaurant_content = hotel_restaurant_results.content.split('Restaurants:')[1] if 'Restaurants:' in hotel_restaurant_results.content else "Fine dining and local cuisine options available"
        st.info(restaurant_content)
    
    # Itinerary Section
    st.markdown('<div class="section-header">🗓️ Your Personalized Itinerary</div>', unsafe_allow_html=True)
    
    # Itinerary in expandable sections
    with st.expander("📅 View Detailed Itinerary", expanded=True):
        st.markdown(itinerary.content)
    
    # Success Message
    st.markdown("""
        <div class="success-banner">
            <h2>✅ Travel Plan Generated Successfully!</h2>
            <p>Your perfect {}-day {} to {} is ready! 🎉</p>
            <p>You can now proceed with bookings and preparations.</p>
        </div>
    """.format(num_days, travel_theme, destination_full), unsafe_allow_html=True)
    
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; margin-top: 2rem; padding: 1rem; background: #f8fafc; border-radius: 8px;'>"
    "✈️Travel Planner • Your Smart Travel Companion • "
    "<a href='#' style='color: #2563eb; text-decoration: none;'>Help</a> • "
    "<a href='#' style='color: #2563eb; text-decoration: none;'>Privacy</a> • "
    "<a href='#' style='color: #2563eb; text-decoration: none;'>Terms</a>"
    "</div>",
    unsafe_allow_html=True
)
