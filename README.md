**🌍 AI Powered Travel Planner**

An intelligent, multi-agent travel orchestration system that automates the creation of personalized itineraries. Powered by Google Gemini 2.0 Flash and the Agno  framework, this application synthesizes real-time flight data, cultural insights, and budget constraints into a cohesive travel plan.

**🚀 Features**
1. Multi-Agent Orchestration: Specialized agents (Researcher, Planner, and Hotel Finder) collaborate to provide comprehensive travel advice.
2. Real-Time Flight Data: Integrated with SerpAPI to fetch live flight schedules and pricing.
3. Dynamic Currency Conversion: Automatically calculates costs in local currencies (PKR, INR, AED, etc.) based on the departure city.
4. Persistent Storage: Saves generated itineraries to a SQLite database for future retrieval.
5. Interactive UI: A modern, responsive dashboard built with Streamlit.

**🛠️ Tech Stack**

Language: Python 3.10+

LLM: Google Gemini 2.0 Flash

Orchestration: Agno (formerly Phidata)

Frontend: Streamlit

Database: SQLite3

External APIs: SerpAPI (Google Search)

**📋 Prerequisites**

Before running the project, ensure you have the following:

Google AI Studio Key: Get it from Google AI Studio.

SerpAPI Key: Get it from SerpAPI.


**⚙️ Installation & Setup**

Clone the repository:

git clone https://github.com/your-username/ai-travel-planner.git

cd ai-travel-planner


Create a virtual environment:

python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate


**Install dependencies:**

pip install -r requirements.txt


Configure Environment Variables:
Create a .env file in the root directory and add your keys:


**Code snippet**

GOOGLE_API_KEY="your_gemini_api_key_here"

SERPAPI_KEY="your_serpapi_key_here"


**🖥️ Usage**

Run the Streamlit application:

streamlit run travel.py

Open your browser to http://localhost:8501 to start planning your trip!

**📂 Project Structure**

├── travel.py              # Main application logic & UI

├── travel_plans.db        # SQLite database for itineraries

├── requirements.txt       # Project dependencies

├── .env                   # API Keys (Internal use only)

└── README.md              # Project documentation


**🛡️ License**

This project is licensed under the MIT License - see the LICENSE file for details.
