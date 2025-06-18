from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient
import os
import asyncio
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
import re
import time
from asyncio import sleep

class ShoppingAssistant:
    """Intelligent AI Shopping Assistant with web search and product comparison capabilities."""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
        
        if not os.environ["GROQ_API_KEY"]:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        
        # Config file path - update this to your browser MCP config
        self.config_file = r"D:\mcp\mcpdemo\browser_mcp.json"
        
        # Initialize MCP components
        self.client = None
        self.agent = None
        self.conversation_context = []
        
        # Rate limiting and error handling
        self.last_search_time = 0
        self.min_search_interval = 3  # Minimum seconds between searches
        self.max_retries = 3
        self.retry_delay = 5
        
        # Product categories and keywords for better query understanding
        self.product_categories = {
            'electronics': ['phone', 'laptop', 'tablet', 'tv', 'camera', 'headphones', 'speaker'],
            'appliances': ['washing machine', 'refrigerator', 'microwave', 'air conditioner', 'purifier'],
            'services': ['netflix', 'amazon prime', 'spotify', 'disney+', 'hulu'],
            'clothing': ['shirt', 'jeans', 'dress', 'shoes', 'jacket'],
            'home': ['furniture', 'decor', 'bedding', 'kitchen', 'bathroom']
        }
        
        # Shopping sites for targeted searches
        self.shopping_sites = [
            'amazon.com', 'flipkart.com', 'ebay.com', 'bestbuy.com', 
            'target.com', 'walmart.com', 'myntra.com', 'ajio.com'
        ]

    async def initialize(self):
        """Initialize the MCP client and agent."""
        print("🚀 Initializing Shopping Assistant...")
        
        try:
            self.client = MCPClient.from_config_file(self.config_file)
            llm = ChatGroq(
                model="qwen-qwq-32b",
                temperature=0.1,  # Very low temperature for stability
                max_tokens=1500,  # Reduced token limit
                max_retries=2,    # Built-in retry mechanism
                request_timeout=30  # Timeout to prevent hanging
            )
            
            # Simplified system prompt to reduce function call complexity
            shopping_system_prompt = """
            You are a helpful Shopping Assistant. When users ask about products:
            
            1. If they ask for current information, use web search ONCE per query
            2. Provide clear, structured responses with:
               - Product features and specifications
               - Price ranges (if found)
               - Pros and cons
               - Recommendations
            
            3. Keep responses concise but informative
            4. If search fails, provide general knowledge and suggest the user check specific retailers
            
            IMPORTANT: Only use tools when absolutely necessary. Prefer using your existing knowledge first.
            """
            
            self.agent = MCPAgent(
                llm=llm,
                client=self.client,
                max_steps=8,  # Reduced steps to prevent errors
                memory_enabled=True,
                system_prompt=shopping_system_prompt
            )
            
            print("✅ Shopping Assistant initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing: {e}")
            raise

    async def safe_search_with_retry(self, query: str) -> Optional[str]:
        """Perform web search with rate limiting and retry logic."""
        # Check rate limiting
        current_time = time.time()
        time_since_last_search = current_time - self.last_search_time
        
        if time_since_last_search < self.min_search_interval:
            wait_time = self.min_search_interval - time_since_last_search
            print(f"⏳ Rate limiting: waiting {wait_time:.1f} seconds...")
            await sleep(wait_time)
        
        for attempt in range(self.max_retries):
            try:
                print(f"🔍 Searching... (attempt {attempt + 1}/{self.max_retries})")
                
                # Create a simple search prompt that's less likely to cause function call errors
                search_prompt = f"Please search the web for information about: {query}"
                
                # Update last search time
                self.last_search_time = time.time()
                
                # Try to get response from agent
                response = await self.agent.run(search_prompt)
                
                if response and "Error" not in response:
                    return response
                else:
                    print(f"⚠️ Search attempt {attempt + 1} returned error or empty result")
                    
            except Exception as e:
                print(f"⚠️ Search attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    print(f"🔄 Retrying in {self.retry_delay} seconds...")
                    await sleep(self.retry_delay)
        
        return None

    def get_fallback_response(self, query: str, analysis: Dict) -> str:
        """Provide fallback response when search fails."""
        category = analysis['category']
        query_types = analysis['query_types']
        
        fallback_responses = {
            'electronics': {
                'comparison': "For electronics comparisons, I recommend checking:\n• GSMArena for phone specs\n• NotebookCheck for laptops\n• RTings for TVs and audio\n• TechRadar for general reviews",
                'recommendation': "For electronics recommendations:\n• Consider your budget and primary use case\n• Check recent reviews on tech sites\n• Compare specifications that matter to you\n• Look for warranty and customer support",
                'default': "For electronics information, check manufacturer websites and tech review sites for the most current specs and pricing."
            },
            'appliances': {
                'comparison': "For appliance comparisons:\n• Consumer Reports for reliability ratings\n• Energy Star ratings for efficiency\n• Manufacturer websites for specifications\n• Home improvement store reviews",
                'recommendation': "When choosing appliances:\n• Consider energy efficiency ratings\n• Check warranty terms\n• Read user reviews for reliability\n• Measure your space before buying",
                'default': "For appliance information, check brand websites and consumer review sites for current models and features."
            },
            'services': {
                'comparison': "For service comparisons:\n• Visit official websites for current pricing\n• Check feature comparison charts\n• Read user reviews on independent sites\n• Consider free trial periods",
                'default': "For service information, check official websites for the most up-to-date pricing and features."
            }
        }
        
        response_type = 'comparison' if 'comparison' in query_types else 'recommendation' if 'recommendation' in query_types else 'default'
        
        base_response = fallback_responses.get(category, {}).get(response_type, 
                                               "I apologize, but I'm having trouble accessing current information right now.")
        
        return f"""
🔍 **Search Temporarily Unavailable**

{base_response}

💡 **General Tips:**
• Check official manufacturer websites for accurate specs
• Compare prices across multiple retailers
• Read recent user reviews and expert opinions
• Consider factors like warranty, customer support, and return policies

Would you like me to help you with a more specific aspect of your query using my general knowledge?
"""

    def categorize_query(self, query: str) -> Dict[str, any]:
        """Analyze the user query to understand intent and product category."""
        query_lower = query.lower()
        
        # Detect query type
        query_types = {
            'comparison': any(word in query_lower for word in ['vs', 'versus', 'compare', 'difference', 'better']),
            'recommendation': any(word in query_lower for word in ['best', 'recommend', 'suggest', 'good', 'top']),
            'features': any(word in query_lower for word in ['features', 'specs', 'specifications', 'details']),
            'price': any(word in query_lower for word in ['price', 'cost', 'cheap', 'expensive', 'budget', 'under', '$']),
            'reviews': any(word in query_lower for word in ['review', 'rating', 'feedback', 'opinion'])
        }
        
        # Detect product category
        detected_category = 'general'
        for category, keywords in self.product_categories.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_category = category
                break
        
        # Extract budget if mentioned
        budget_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', query)
        budget = budget_match.group(1) if budget_match else None
        
        return {
            'query_types': [qtype for qtype, detected in query_types.items() if detected],
            'category': detected_category,
            'budget': budget,
            'original_query': query
        }

    def enhance_search_query(self, original_query: str, analysis: Dict) -> str:
        """Enhance the search query for better product results."""
        enhanced_query = original_query
        
        # Add current year for latest products
        current_year = datetime.now().year
        if analysis['category'] == 'electronics':
            enhanced_query += f" {current_year} latest model"
        
        # Add review keywords for better results
        if 'recommendation' in analysis['query_types']:
            enhanced_query += " reviews comparison best"
        
        # Add pricing keywords
        if 'price' in analysis['query_types'] and analysis['budget']:
            enhanced_query += f" under ${analysis['budget']} price"
        
        return enhanced_query

    async def process_shopping_query(self, user_query: str) -> str:
        """Process shopping-related queries with enhanced error handling."""
        try:
            # Analyze the query
            query_analysis = self.categorize_query(user_query)
            
            print(f"🔍 Query Analysis: {query_analysis['query_types']} | Category: {query_analysis['category']}")
            
            # Try to get current information via search
            search_result = await self.safe_search_with_retry(user_query)
            
            if search_result:
                print("✅ Successfully retrieved current information")
                response = search_result
            else:
                print("⚠️ Search unavailable, using fallback response")
                response = self.get_fallback_response(user_query, query_analysis)
            
            # Store conversation context
            self.conversation_context.append({
                'query': user_query,
                'analysis': query_analysis,
                'response': response[:200] + "..." if len(response) > 200 else response,
                'timestamp': datetime.now().isoformat(),
                'search_successful': search_result is not None
            })
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Error processing query: {str(e)}"
            print(error_msg)
            
            # Provide helpful fallback
            return f"""
{error_msg}

🔄 **Alternative Suggestions:**
• Try rephrasing your question more simply
• Ask about specific product features instead of comparisons
• Check the manufacturer's official website
• Visit retailer websites for current pricing and availability

Would you like to try a different question?
"""

    def get_conversation_summary(self) -> str:
        """Get a summary of recent conversation for context."""
        if not self.conversation_context:
            return "No previous conversation."
        
        recent_queries = self.conversation_context[-3:]  # Last 3 queries
        summary = "Recent conversation:\n"
        for item in recent_queries:
            summary += f"- Asked about: {item['query'][:50]}...\n"
        
        return summary

    async def run_interactive_chat(self):
        """Run the interactive shopping assistant chat."""
        print("\n" + "="*60)
        print("🛍️  INTELLIGENT SHOPPING ASSISTANT CHATBOT  🛍️")
        print("="*60)
        print("I can help you with:")
        print("• Product comparisons and recommendations")
        print("• Feature analysis and specifications")
        print("• Price research and deals")
        print("• Service comparisons (Netflix, Amazon Prime, etc.)")
        print("• Purchase advice based on your needs")
        print("\n⚠️  Note: Search may be rate-limited. I'll provide fallback info if needed.")
        print("\nCommands:")
        print("• Type 'exit' or 'quit' to end")
        print("• Type 'clear' to clear conversation history")
        print("• Type 'context' to see conversation summary")
        print("• Type 'status' to check system status")
        print("="*60 + "\n")
        
        try:
            while True:
                user_input = input("\n🛒 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit"]:
                    print("\n👋 Thank you for using Shopping Assistant! Happy shopping!")
                    break
                
                if user_input.lower() == "clear":
                    self.agent.clear_conversation_history()
                    self.conversation_context.clear()
                    print("🧹 Conversation history cleared.")
                    continue
                
                if user_input.lower() == "context":
                    print(f"\n📋 {self.get_conversation_summary()}")
                    continue
                
                if user_input.lower() == "status":
                    last_search_ago = time.time() - self.last_search_time if self.last_search_time > 0 else float('inf')
                    print(f"\n📊 System Status:")
                    print(f"• Last search: {last_search_ago:.1f} seconds ago")
                    print(f"• Rate limit interval: {self.min_search_interval} seconds")
                    print(f"• Conversations stored: {len(self.conversation_context)}")
                    continue
                
                print("\n🤖 Assistant: ", end="", flush=True)
                
                try:
                    # Process the shopping query with improved error handling
                    response = await self.process_shopping_query(user_input)
                    print(response)
                    
                except KeyboardInterrupt:
                    print("\n🛑 Query interrupted by user.")
                    continue
                    
                except Exception as e:
                    print(f"❌ Unexpected error: {str(e)}")
                    print("🔄 Please try a simpler question or check your internet connection.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Shopping Assistant interrupted. Goodbye!")
        
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Clean up resources."""
        if self.client and self.client.sessions:
            await self.client.close_all_sessions()
            print("🧹 Resources cleaned up.")

async def main():
    """Main function to run the shopping assistant."""
    assistant = ShoppingAssistant()
    
    try:
        await assistant.initialize()
        await assistant.run_interactive_chat()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Example usage and test queries
    print("🚀 Starting Intelligent Shopping Assistant...")
    print("\nExample queries you can try:")
    print("• 'What are the features of iPhone 15 vs Samsung S24?'")
    print("• 'Which air purifier is best under $200?'")
    print("• 'Tell me about the latest washing machines from LG'")
    print("• 'Compare Netflix and Amazon Prime in terms of content and pricing'")
    print("• 'Best laptop for programming under $1000'")
    print("• 'Sony WH-1000XM5 vs Bose QuietComfort 45 headphones'")
    
    asyncio.run(main())