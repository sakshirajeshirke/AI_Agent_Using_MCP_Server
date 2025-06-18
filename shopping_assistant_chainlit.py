import chainlit as cl
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os
import asyncio
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
import re
import time

class ShoppingAssistant:
    """Intelligent AI Shopping Assistant with web search and product comparison capabilities."""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        
        # Initialize LLM directly without MCP for now to avoid context issues
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",  # Changed to a more stable model
            temperature=0.1,
            max_tokens=1500,
            max_retries=2,
            request_timeout=30,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        self.conversation_history = []
        
        # Rate limiting
        self.last_search_time = 0
        self.min_search_interval = 2
        
        # Product categories for better understanding
        self.product_categories = {
            'electronics': ['phone', 'laptop', 'tablet', 'tv', 'camera', 'headphones', 'speaker', 'iphone', 'samsung', 'sony'],
            'appliances': ['washing machine', 'refrigerator', 'microwave', 'air conditioner', 'purifier', 'dishwasher'],
            'services': ['netflix', 'amazon prime', 'spotify', 'disney+', 'hulu', 'streaming'],
            'clothing': ['shirt', 'jeans', 'dress', 'shoes', 'jacket', 'nike', 'adidas'],
            'home': ['furniture', 'decor', 'bedding', 'kitchen', 'bathroom', 'sofa', 'table']
        }

    async def initialize(self):
        """Initialize the shopping assistant."""
        try:
            # Test the LLM connection
            test_response = await self.llm.ainvoke("Hello, are you ready to help with shopping queries?")
            return True
        except Exception as e:
            print(f"Initialization error: {e}")
            return False

    def categorize_query(self, query: str) -> Dict[str, any]:
        """Analyze the user query to understand intent and product category."""
        query_lower = query.lower()
        
        # Detect query type
        query_types = []
        if any(word in query_lower for word in ['vs', 'versus', 'compare', 'difference', 'better']):
            query_types.append('comparison')
        if any(word in query_lower for word in ['best', 'recommend', 'suggest', 'good', 'top']):
            query_types.append('recommendation')
        if any(word in query_lower for word in ['features', 'specs', 'specifications', 'details']):
            query_types.append('features')
        if any(word in query_lower for word in ['price', 'cost', 'cheap', 'expensive', 'budget', 'under', '$']):
            query_types.append('price')
        if any(word in query_lower for word in ['review', 'rating', 'feedback', 'opinion']):
            query_types.append('reviews')
        
        # Detect product category
        detected_category = 'general'
        for category, keywords in self.product_categories.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_category = category
                break
        
        # Extract budget
        budget_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', query)
        budget = budget_match.group(1) if budget_match else None
        
        return {
            'query_types': query_types,
            'category': detected_category,
            'budget': budget,
            'original_query': query
        }

    async def get_smart_response(self, user_query: str, analysis: Dict) -> str:
        """Get intelligent response using LLM with shopping context."""
        
        # Build context-aware prompt
        system_context = f"""
You are an expert Shopping Assistant. The user is asking about: {analysis['category']} products.
Query type: {', '.join(analysis['query_types']) if analysis['query_types'] else 'general inquiry'}
Budget mentioned: ${analysis['budget']} if analysis['budget'] else 'not specified'

Provide helpful, detailed information about:
- Product features and specifications
- Price ranges and value for money
- Pros and cons
- Recommendations based on use cases
- Where to buy or what to look for

Be specific, practical, and honest. If you don't have current pricing, mention that prices may vary and suggest checking current retailers.

User Query: {user_query}
"""

        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_search_time < self.min_search_interval:
                await asyncio.sleep(self.min_search_interval - (current_time - self.last_search_time))
            
            self.last_search_time = time.time()
            
            # Get response from LLM
            response = await self.llm.ainvoke(system_context)
            
            # Store in conversation history
            self.conversation_history.append({
                'query': user_query,
                'response': response.content[:200] + "..." if len(response.content) > 200 else response.content,
                'timestamp': datetime.now().isoformat(),
                'category': analysis['category']
            })
            
            return response.content
            
        except Exception as e:
            return self.get_fallback_response(user_query, analysis)

    def get_fallback_response(self, query: str, analysis: Dict) -> str:
        """Provide fallback response when LLM fails."""
        category = analysis['category']
        query_types = analysis['query_types']
        
        fallback_responses = {
            'electronics': {
                'comparison': """
🔍 **Electronics Comparison Tips:**

For comparing electronics, I recommend checking:
• **GSMArena** - For phone specifications and comparisons
• **NotebookCheck** - Comprehensive laptop reviews and benchmarks  
• **RTings** - In-depth TV, monitor, and audio equipment testing
• **TechRadar & The Verge** - Latest reviews and buying guides

**Key factors to compare:**
• Performance benchmarks and real-world usage
• Battery life and efficiency
• Build quality and durability
• Price-to-performance ratio
• Warranty and customer support
                """,
                'recommendation': """
🏆 **Electronics Buying Guide:**

**Before buying electronics:**
• Set a clear budget range
• Define your primary use cases
• Check recent reviews from multiple sources
• Compare specifications that matter to you
• Look for seasonal sales and discounts

**Reliable brands to consider:**
• **Phones:** Apple, Samsung, Google, OnePlus
• **Laptops:** Apple, Dell, Lenovo, ASUS, HP
• **Audio:** Sony, Bose, Sennheiser, Audio-Technica
                """,
                'default': """
💡 **Electronics Shopping Tips:**

• Check manufacturer websites for official specs
• Read both expert reviews and user feedback
• Compare prices across multiple retailers
• Consider refurbished options for savings
• Check warranty terms and return policies
• Look for bundle deals and accessories
                """
            },
            'appliances': {
                'comparison': """
🏠 **Appliance Comparison Guide:**

**Research resources:**
• **Consumer Reports** - Reliability and performance ratings
• **Energy Star** - Energy efficiency comparisons
• **Home improvement stores** - Customer reviews and ratings

**Key comparison factors:**
• Energy efficiency ratings (save on utilities)
• Capacity and size for your space
• Warranty coverage and service network
• User reviews for long-term reliability
                """,
                'recommendation': """
✨ **Smart Appliance Shopping:**

**Essential considerations:**
• Measure your space before shopping
• Check energy efficiency ratings (save money long-term)
• Read reliability reviews and ratings
• Consider smart features vs. simplicity
• Factor in installation and delivery costs

**Top appliance brands:**
• **Refrigerators:** Samsung, LG, Whirlpool
• **Washing Machines:** LG, Samsung, Bosch
• **Kitchen:** KitchenAid, Bosch, GE
                """,
                'default': """
🔧 **Appliance Shopping Essentials:**

• Measure your space carefully
• Check energy efficiency ratings
• Read long-term reliability reviews  
• Compare warranty terms
• Consider professional installation needs
• Look for seasonal sales events
                """
            },
            'services': {
                'comparison': """
📺 **Streaming Service Comparison:**

**Compare these factors:**
• **Content library** - Movies, shows, originals
• **Pricing tiers** - Monthly costs and features
• **Video quality** - 4K, HDR support
• **Device compatibility** - Your TV, phone, etc.
• **Simultaneous streams** - How many devices
• **Offline downloads** - For mobile viewing

**Popular services:**
• **Netflix** - Largest content library, strong originals
• **Amazon Prime** - Includes shopping benefits
• **Disney+** - Family content, Marvel, Star Wars
• **HBO Max** - Premium content and movies
                """,
                'default': """
🎬 **Service Selection Tips:**

• Try free trials before committing
• Check what content you actually watch
• Consider bundle deals (Disney+, Hulu, ESPN+)
• Look for annual subscription discounts
• Review and cancel unused subscriptions regularly
                """
            }
        }
        
        response_type = 'comparison' if 'comparison' in query_types else 'recommendation' if 'recommendation' in query_types else 'default'
        
        base_response = fallback_responses.get(category, {}).get(response_type, 
                                               fallback_responses['electronics']['default'])
        
        return f"""
⚠️ **Currently using offline knowledge** - For the most current information, please check official websites.

{base_response}

💡 **General Shopping Tips:**
• Check official manufacturer websites for accurate specs
• Compare prices across multiple retailers (Amazon, Best Buy, etc.)
• Read recent user reviews and expert opinions
• Consider warranty, return policy, and customer support
• Look for seasonal sales and discount codes

Would you like me to help you with a more specific aspect of your query?
"""

    async def process_shopping_query(self, user_query: str) -> str:
        """Process shopping queries with improved error handling."""
        try:
            # Analyze the query
            analysis = self.categorize_query(user_query)
            
            # Get intelligent response
            response = await self.get_smart_response(user_query, analysis)
            
            return response
            
        except Exception as e:
            # Return helpful error message
            return f"""
❌ **Temporary Issue**: {str(e)}

🔄 **What you can try:**
• Rephrase your question more simply
• Ask about specific product features
• Check manufacturer websites directly
• Try again in a moment

**Example queries that work well:**
• "Compare iPhone 15 vs Samsung Galaxy S24"
• "Best laptop for programming under $1000"
• "Netflix vs Amazon Prime features"

Would you like to try a different question?
"""

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()

    def get_stats(self):
        """Get conversation statistics."""
        if not self.conversation_history:
            return "No conversations yet."
        
        categories = {}
        for conv in self.conversation_history:
            cat = conv.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        stats = f"**Conversation Stats:**\n"
        stats += f"• Total queries: {len(self.conversation_history)}\n"
        for cat, count in categories.items():
            stats += f"• {cat.title()}: {count}\n"
        
        return stats

# Initialize global assistant
shopping_assistant = None

@cl.on_chat_start
async def start():
    """Initialize the shopping assistant when chat starts."""
    global shopping_assistant
    
    # Send welcome message
    welcome_message = """
# 🛍️ Welcome to Your AI Shopping Assistant! 

I'm here to help you make informed shopping decisions with:

## 🎯 **What I Can Help With:**
- **Product Comparisons** - iPhone vs Samsung, laptop comparisons, etc.
- **Buying Recommendations** - Best products for your needs and budget
- **Feature Analysis** - Detailed specifications and capabilities
- **Price Guidance** - Value for money and budget considerations
- **Service Comparisons** - Netflix vs Amazon Prime, streaming services

## 🔥 **Try These Examples:**
- *"Compare iPhone 15 vs Samsung Galaxy S24"*
- *"Best laptop for programming under $1000"*
- *"Sony WH-1000XM5 vs Bose QuietComfort 45"*
- *"Netflix vs Amazon Prime comparison"*
- *"Which air purifier is best for allergies?"*

## 🎮 **Commands:**
- Type **`help`** - Show available commands
- Type **`clear`** - Clear conversation history
- Type **`stats`** - Show conversation statistics

*Ready to help you shop smarter! What are you looking for today?*
"""
    
    await cl.Message(
        content=welcome_message,
        author="Shopping Assistant"
    ).send()
    
    # Initialize the shopping assistant
    shopping_assistant = ShoppingAssistant()
    
    # Show initialization status
    init_msg = cl.Message(content="🚀 Initializing AI assistant...", author="System")
    await init_msg.send()
    
    try:
        success = await shopping_assistant.initialize()
        if success:
            init_msg.content = "✅ Shopping Assistant ready! Ask me anything about products or services."
        else:
            init_msg.content = "⚠️ Assistant initialized with basic features. I can still help with shopping advice!"
        await init_msg.update()
    except Exception as e:
        init_msg.content = f"⚠️ Assistant running in offline mode. Still ready to help! ({str(e)})"
        await init_msg.update()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""
    global shopping_assistant
    
    if not shopping_assistant:
        await cl.Message(
            content="❌ Shopping Assistant not initialized. Please refresh the page.",
            author="System"
        ).send()
        return
    
    user_query = message.content.strip()
    
    # Handle special commands
    if user_query.lower() == "clear":
        shopping_assistant.clear_history()
        await cl.Message(
            content="🧹 **Conversation history cleared!** Ready for new shopping questions.",
            author="System"
        ).send()
        return
    
    if user_query.lower() == "stats":
        stats = shopping_assistant.get_stats()
        await cl.Message(
            content=f"📊 {stats}",
            author="System"
        ).send()
        return
    
    if user_query.lower() == "help":
        help_message = """
## 🛍️ Shopping Assistant Help

### 🔍 **Product Research:**
- *"Compare [Product A] vs [Product B]"*
- *"Best [product] under $[budget]"*
- *"[Product name] features and specs"*
- *"Is [product] worth buying?"*

### 📱 **Example Queries:**
- *"iPhone 15 vs Samsung Galaxy S24 camera comparison"*
- *"Best gaming laptop under $1500"*
- *"Sony WH-1000XM5 headphones review"*
- *"Netflix vs Amazon Prime which is better"*
- *"Air purifier recommendations for allergies"*

### 🎮 **Commands:**
- **`clear`** - Clear conversation history
- **`stats`** - Show conversation statistics  
- **`help`** - Show this help message

### 💡 **Tips for Better Results:**
- Be specific about your needs and budget
- Mention your use case (gaming, work, family, etc.)
- Ask follow-up questions for more details
- I can help with electronics, appliances, services, and more!

**What would you like to know about?**
"""
        await cl.Message(
            content=help_message,
            author="Shopping Assistant"
        ).send()
        return
    
    # Process shopping query with visual feedback
    async with cl.Step(name="🔍 Analyzing your shopping query", type="tool") as step:
        try:
            # Analyze query first
            analysis = shopping_assistant.categorize_query(user_query)
            step.output = f"Detected: {analysis['category']} - {', '.join(analysis['query_types']) if analysis['query_types'] else 'general inquiry'}"
            
        except Exception as e:
            step.output = f"Analysis error: {str(e)}"
    
    # Get and send response
    async with cl.Step(name="🤖 Generating shopping advice", type="llm") as step:
        try:
            response = await shopping_assistant.process_shopping_query(user_query)
            step.output = "Generated personalized shopping advice"
            
        except Exception as e:
            step.output = f"Error: {str(e)}"
            response = f"❌ Sorry, I encountered an error: {str(e)}\n\nPlease try rephrasing your question or ask something else."
    
    # Send the response
    await cl.Message(
        content=response,
        author="Shopping Assistant"
    ).send()

@cl.on_chat_end
async def end():
    """Cleanup when chat ends."""
    global shopping_assistant
    if shopping_assistant:
        shopping_assistant.clear_history()
        print("Chat session ended and cleaned up.")

if __name__ == "__main__":
    # Run with: chainlit run shopping_assistant_chainlit.py
    pass