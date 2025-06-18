AI Shopping Assistant
Overview
The AI Shopping Assistant is an intelligent, interactive tool powered by the Grok AI model from xAI, integrated with the MCP (Multi-Context Platform) framework for enhanced web search capabilities. It assists users in making informed shopping decisions by providing product comparisons, recommendations, feature analyses, and price guidance across categories such as electronics, appliances, services, clothing, and home goods. The assistant uses natural language processing to categorize queries and deliver tailored responses, with robust error handling and fallback mechanisms.
Features

Product Comparisons: Compare features, specs, and prices (e.g., iPhone 15 vs. Samsung Galaxy S24).
Recommendations: Suggest products based on user needs and budget (e.g., best laptop under $1000).
Feature Analysis: Provide detailed specifications and capabilities.
Price Guidance: Offer insights on value for money and budget considerations.
Service Comparisons: Compare streaming services like Netflix vs. Amazon Prime.
Web Search Integration: Uses MCP for targeted web searches on shopping sites (e.g., Amazon, Flipkart, Best Buy).
Conversation Context: Maintains query history for context-aware responses and provides conversation summaries.
Commands: Supports exit, clear, context, and status for interactive chat control.
Rate Limiting & Retries: Ensures responsible API usage with a 3-second interval between searches and up to 3 retries.
Fallback Responses: Delivers offline, category-specific advice when searches fail.

Prerequisites

Python 3.8 or higher
A Grok API key from xAI (set as GROQ_API_KEY in environment variables)
Node.js and npm for running MCP servers
Required Python packages (listed in requirements.txt)
MCP configuration file (browser_mcp.json) for web search functionality

Installation

Clone the Repository:
git clone <repository-url>
cd ai-shopping-assistant


Set Up a Virtual Environment (optional but recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Python Dependencies:
pip install -r requirements.txt


Install Node.js Dependencies for MCP:Ensure Node.js and npm are installed, then install MCP server packages:
npm install -g @playwright/mcp @openbnb/mcp-server-airbnb duckduckgo-mcp-server


Set Up Environment Variables:Create a .env file in the project root with your Grok API key:
echo "GROQ_API_KEY=your-api-key-here" > .env


Configure MCP:Place the browser_mcp.json file in the specified directory (e.g., D:\mcp\mcpdemo\). The provided MCP configuration is:
{
    "mcpServers": {
        "playwright": {
            "command": "npx",
            "args": ["@playwright/mcp@latest"]
        },
        "airbnb": {
            "command": "npx",
            "args": ["-y", "@openbnb/mcp-server-airbnb"]
        },
        "duckduckgo-search": {
            "command": "npx",
            "args": ["-y", "duckduckgo-mcp-server"]
        }
    }
}

Update the config_file path in shopping_assistant.py to match your setup:
self.config_file = r"path/to/your/browser_mcp.json"



Usage

Run the Application:
python shopping_assistant.py

This starts the interactive console-based chatbot.

Interact with the Assistant:

Follow the on-screen instructions to enter shopping queries.
Example queries:
"What are the features of iPhone 15 vs Samsung S24?"
"Which air purifier is best under $200?"
"Compare Netflix and Amazon Prime in terms of content and pricing"


Use commands:
exit or quit: End the session.
clear: Clear conversation history.
context: View recent conversation summary.
status: Check system status (e.g., last search time, rate limit).




Example Output:
🛍️  INTELLIGENT SHOPPING ASSISTANT CHATBOT  🛍️
I can help you with:
• Product comparisons and recommendations
• Feature analysis and specifications
• Price research and deals
• Service comparisons (Netflix, Amazon Prime, etc.)
• Purchase advice based on your needs
...
🛒 You: Best laptop for programming under $1000
🤖 Assistant: 🔍 Searching... (attempt 1/3)
✅ Successfully retrieved current information
[Detailed response with laptop recommendations, features, and prices]



Project Structure
ai-shopping-assistant/
├── shopping_assistant.py          # Main application script
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (not tracked in git)
├── browser_mcp.json              # MCP configuration file
└── README.md                     # This file

Requirements
Create a requirements.txt file with the following dependencies:
langchain-grok==0.1.0
python-dotenv==1.0.0
requests==2.31.0
mcp-use==<latest-version>  # Ensure you have the correct MCP package

Configuration

Model: Uses qwen-qwq-32b from Grok, configurable in the ShoppingAssistant class.
Rate Limiting: 3-second minimum interval between searches, with 3 retries and 5-second delay between retries.
Environment Variables:
GROQ_API_KEY: Required for Grok API access.


MCP Configuration: Defined in browser_mcp.json for Playwright, Airbnb, and DuckDuckGo search servers.
Product Categories: Predefined categories (electronics, appliances, services, clothing, home) for query classification.
Shopping Sites: Targeted searches on sites like Amazon, Flipkart, eBay, and Best Buy.

Error Handling

Rate Limiting: Prevents API overload with a 3-second interval between searches.
Retries: Up to 3 attempts for failed searches with a 5-second delay.
Fallback Responses: Category-specific offline advice when searches fail (e.g., API downtime, network issues).
User Guidance: Prompts users to rephrase queries or check retailer websites on errors.

Limitations

Requires an active internet connection for API calls and MCP web searches.
Pricing data may not be real-time; users should verify with retailers.
Limited to predefined product categories; other queries are treated as general.
MCP setup requires correct configuration and Node.js dependencies.
Fallback responses may lack the depth of live search results.

Future Enhancements

Integrate real-time price scraping from retailers.
Expand product categories and shopping sites.
Add user profile personalization for recommendations.
Develop a web-based UI for broader accessibility.
Enhance MCP search with more targeted site-specific queries.

Contributing
Contributions are welcome! Please:

Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit your changes (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a pull request.

