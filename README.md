Here's a more polished and **visually appealing `README.md`** for your **AI Shopping Assistant** project. It features improved formatting, consistent structure, badges (if you'd like to add later), emoji enhancements, and a clear section hierarchy:

---

# 🛍️ AI Shopping Assistant

**An intelligent, conversational shopping assistant powered by the Grok AI model and Model Context Protocol (MCP) for smart web-based product discovery and decision-making.**

---

## ✨ Overview

The **AI Shopping Assistant** is an interactive, AI-powered chatbot that helps users make **smarter shopping decisions**. Backed by **xAI’s Grok LLM** and the **Model Context Protocol (MCP)**, it can:

* 🧠 Understand natural language queries
* 🔎 Conduct real-time searches on shopping platforms
* 🛒 Compare products, services, and features
* 💸 Provide price guidance and recommendations

Whether you're choosing between phones, comparing streaming services, or searching for the best air purifier under a budget—this assistant is your **ultimate shopping buddy**.

---

## 🧩 Features

| Feature                      | Description                                                 |
| ---------------------------- | ----------------------------------------------------------- |
| 🔄 **Product Comparison**    | Compare products (e.g., *iPhone 15 vs. Galaxy S24*)         |
| 🎯 **Smart Recommendations** | Get suggestions based on your needs and budget              |
| 📊 **Feature Analysis**      | Understand specs, pros, cons, and more                      |
| 💵 **Price Guidance**        | Determine best value options                                |
| 🌐 **Service Comparison**    | Compare services like *Netflix vs. Prime Video*             |
| 🔍 **Web Search (via MCP)**  | Searches shopping platforms like Amazon, Flipkart, Best Buy |
| 💬 **Context-Aware Chat**    | Maintains conversation context and provides summaries       |
| 🔁 **Retries & Fallbacks**   | Smart handling of failed searches with category advice      |
| 💡 **Chat Commands**         | `/exit`, `/clear`, `/context`, `/status` supported          |

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-shopping-assistant
```

### 2. Set Up a Virtual Environment (Optional)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install MCP Node.js Dependencies

Make sure **Node.js** and **npm** are installed:

```bash
npm install -g @playwright/mcp @openbnb/mcp-server-airbnb duckduckgo-mcp-server
```

### 5. Environment Setup

Create a `.env` file in the root directory:

```bash
echo "GROQ_API_KEY=your-api-key-here" > .env
```

### 6. MCP Configuration

Ensure you have a valid `browser_mcp.json` in your MCP directory (e.g., `D:\mcp\mcpdemo\`):

```json
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
```

In `shopping_assistant.py`, set:

```python
self.config_file = r"path/to/your/browser_mcp.json"
```

---

## 🧠 Usage

### Start the Assistant:

```bash
python shopping_assistant.py
```

### Example Queries:

```text
🛒 You: Best laptop for programming under $1000  
🤖 Assistant: 🔍 Searching... (attempt 1/3)  
✅ Successfully retrieved current information  
[Laptop recommendations with specs and prices]
```

### Commands You Can Use:

* `exit` or `quit` – End the session
* `clear` – Reset chat history
* `context` – View recent conversation summary
* `status` – Check last search time and rate limits

---

## 🗂️ Project Structure

```
ai-shopping-assistant/
├── shopping_assistant.py      # Main assistant logic
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── browser_mcp.json           # MCP config for search engines
└── README.md                  # You're reading it!
```

---

## 📦 Requirements

Add the following to your `requirements.txt`:

```
langchain-grok==0.1.0
python-dotenv==1.0.0
requests==2.31.0
mcp-use==<latest-version>
```

---

## ⚙️ Configuration Details

| Setting               | Description                                       |
| --------------------- | ------------------------------------------------- |
| 🔑 **GROQ\_API\_KEY** | Set in `.env` for xAI’s Grok access               |
| 🕒 **Rate Limiting**  | 3-second delay between API searches               |
| 🔁 **Retries**        | Up to 3 search retries with 5s backoff            |
| 📁 **MCP File**       | JSON config for search integration                |
| 📦 **Model**          | Default: `qwen-qwq-32b` (Grok model)              |
| 🛍️ **Categories**    | Electronics, appliances, services, clothing, home |

---

## ⚠️ Limitations

* Requires internet connection for API and MCP search
* Prices may vary—verify with retailers
* Only predefined categories supported
* MCP setup requires proper Node.js configuration
* Offline fallbacks may offer limited depth

---

## 🔮 Future Enhancements

* 🛒 Real-time price scraping from major e-retailers
* 🧬 Personalized recommendations via user profiles
* 🖥️ Web-based UI for a seamless UX
* 🛠️ Enhanced MCP integration with more shopping portals

---

## 🤝 Contributing

Contributions are welcome!
To contribute:

1. Fork the repository
2. Create your feature branch

   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes

   ```bash
   git commit -m "Add your feature"
   ```
4. Push and open a PR

   ```bash
   git push origin feature/your-feature
   ```

---

---

> 🧠 **AI + Shopping = Smarter Choices**
> Start your intelligent shopping journey now with the AI Shopping Assistant.
