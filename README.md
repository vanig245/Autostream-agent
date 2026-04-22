# AutoStream AI Agent 

A conversational AI agent that converts social media conversations into 
qualified business leads for AutoStream — an automated video editing SaaS platform.

---

## Demo
The agent can:
- Answer pricing and feature questions using RAG
- Detect high-intent users ready to sign up
- Collect Name, Email, Platform details
- Trigger lead capture automatically

---

## Tech Stack
- Python 3.13
- LangGraph (State Management)
- LangChain (AI Framework)
- Groq — LLaMA 3.3 70B (LLM)
- JSON Knowledge Base (RAG)

---

---

## Project Structure

```text
autostream-agent/
├── knowledge_base/
│   └── autostream_kb.json      # Pricing & policies data
├── agent/
│   ├── __init__.py             # Package init
│   ├── rag.py                  # RAG pipeline
│   ├── tools.py                # Lead capture tool
│   └── agent.py                # Main agent logic
├── main.py                     # Entry point
├── requirements.txt            # Dependencies
└── README.md

---

## How to Run Locally

### 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/autostream-agent.git
cd autostream-agent

### 2. Create virtual environment
python3 -m venv .venv

# Mac/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

Open .env and add your API key:
GROQ_API_KEY=your_groq_api_key_here

Get free Groq API key at: https://console.groq.com

### 5. Run the agent
python3 main.py

---

## Sample Conversation


  Welcome to AutoStream AI Assistant 🎬


You: Hi there!
Agent: Welcome to AutoStream! We help content creators automate 
       their video editing. How can I help you today?

You: What are your pricing plans?
Agent: Here are our plans:
       Basic Plan - $29/month: 10 videos, 720p resolution
       Pro Plan - $79/month: Unlimited videos, 4K, AI captions, 24/7 support

You: The Pro plan sounds great, I want to sign up for my YouTube channel!
Agent: Amazing! Let's get you started. May I have your full name?

You: John Doe
Agent: Thanks John! What's your email address?

You: john@gmail.com
Agent: Perfect! Which platform do you create content on?

You: YouTube
Agent: 🎉 You're all set! Our team will reach out within 24 hours!


LEAD CAPTURED SUCCESSFULLY!
Name     : John Doe
Email    : john@gmail.com
Platform : YouTube


---

## Architecture Explanation

This agent is built using LangGraph — a framework that manages AI 
agent workflows as a state graph. LangGraph was chosen because it allows 
the agent to maintain full conversation state across multiple turns, making 
it ideal for multi-step flows like lead collection where the agent needs 
to remember previously collected information.

### How it works:

The architecture has three main nodes connected in a graph:

1. **detect_intent** — Classifies user message into greeting, 
   product_inquiry, or high_intent using keyword matching

2. **generate_response** — Uses LLaMA 3.3 via Groq with RAG context 
   to answer questions accurately from the knowledge base

3. **collect_lead_info** — Progressively collects name, email, 
   and platform one by one with validation

### State Management:
State is managed using a TypedDict called AgentState which stores:
- Full conversation history (messages list)
- Detected intent
- Collected lead fields (name, email, platform)
- Progress flags (collecting_lead, last_asked, lead_captured)

This state is passed between nodes on every turn, giving the agent 
complete memory across 5-6 conversation turns as required.

### RAG Pipeline:
The RAG pipeline retrieves relevant information from a local JSON 
knowledge base using keyword matching. When a user asks about pricing 
or features, the agent pulls only the relevant section and injects it 
into the LLM prompt — ensuring accurate, hallucination-free answers.

---

## WhatsApp Deployment via Webhooks

To integrate this agent with WhatsApp using webhooks:

1. **Meta Developer Setup** — Create a Meta Developer App at 
   developers.facebook.com, add WhatsApp Business API, and get 
   the Access Token and Phone Number ID.

2. **Build Webhook Server** — Create a FastAPI server with two endpoints:
   - GET /webhook → Meta verifies your server using a challenge token
   - POST /webhook → Receives all incoming WhatsApp messages

3. **Connect Agent** — When a message arrives, extract the user's phone 
   number and message from Meta's payload, pass to LangGraph agent, 
   get the response.

4. **Session Management** — Store each user's AgentState in a dictionary 
   keyed by phone number so every user has their own conversation memory.

5. **Send Reply** — Use WhatsApp Cloud API /messages endpoint to send 
   the agent's response back to the user.

6. **Public URL** — Use ngrok for local testing or deploy on Railway/Render 
   for production so Meta can reach your webhook URL.
