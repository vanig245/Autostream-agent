import os
from typing import TypedDict, Optional, List
from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END

from agent.rag import retrieve_context
from agent.tools import mock_lead_capture, validate_email, validate_name, validate_platform

# Load environment variables
load_dotenv()

# ─────────────────────────────────────────────
# Initialize Gemini LLM
# ─────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)

# ─────────────────────────────────────────────
# State Definition — what agent remembers
# ─────────────────────────────────────────────
class AgentState(TypedDict):
    messages: List[dict]           # full conversation history
    intent: Optional[str]          # greeting / product_inquiry / high_intent
    lead_name: Optional[str]       # collected name
    lead_email: Optional[str]      # collected email
    lead_platform: Optional[str]   # collected platform
    lead_captured: bool            # whether lead is saved
    collecting_lead: bool          # whether currently in lead collection mode
    last_asked: Optional[str]      # what we last asked user for


# ─────────────────────────────────────────────
# Node 1: Detect User Intent
# ─────────────────────────────────────────────
def detect_intent(state: AgentState) -> AgentState:
    """Detect what the user wants"""

    last_message = state["messages"][-1]["content"].lower()

    # High intent keywords
    high_intent_words = [
        "sign up", "signup", "subscribe", "buy", "purchase", "want to try",
        "i want", "let's go", "sounds good", "i'm in", "take it",
        "pro plan", "get started", "register", "enroll"
    ]

    # Product inquiry keywords
    inquiry_words = [
        "price", "plan", "cost", "feature", "how much", "what is",
        "tell me", "explain", "refund", "support", "difference", "compare",
        "4k", "caption", "resolution", "about", "works"
    ]

    # Greeting keywords
    greeting_words = ["hi", "hello", "hey", "good morning", "good evening", "howdy", "sup"]

    if any(word in last_message for word in high_intent_words):
        state["intent"] = "high_intent"
    elif any(word in last_message for word in inquiry_words):
        state["intent"] = "product_inquiry"
    elif any(word in last_message for word in greeting_words):
        state["intent"] = "greeting"
    else:
        state["intent"] = "general"

    return state


# ─────────────────────────────────────────────
# Node 2: Generate AI Response using Gemini
# ─────────────────────────────────────────────
def generate_response(state: AgentState) -> AgentState:
    """Use Gemini to generate a response based on intent and context"""

    intent = state["intent"]
    last_user_message = state["messages"][-1]["content"]

    # Build conversation history for Gemini
    chat_history = []
    for msg in state["messages"][:-1]:  # all except last
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_history.append(AIMessage(content=msg["content"]))

    # Build system prompt based on intent
    if intent == "greeting":
        system_prompt = """You are AutoStream's friendly AI sales assistant.
        The user just greeted you. Welcome them warmly and briefly mention that AutoStream
        helps content creators with automated video editing. Ask how you can help them.
        Keep it short and friendly."""
        context = ""

    elif intent == "product_inquiry":
        context = retrieve_context(last_user_message)
        system_prompt = f"""You are AutoStream's knowledgeable AI sales assistant.
        Answer the user's question using ONLY the information provided below.
        Be helpful, clear and concise. If they seem interested, gently mention they can sign up.
        
        KNOWLEDGE BASE:
        {context}"""

    elif intent == "high_intent":
        system_prompt = """You are AutoStream's AI sales assistant.
        The user wants to sign up! Express excitement and tell them you'll help them get started.
        Tell them you need to collect a few details. Then ask for their FULL NAME first.
        Only ask for name in this message."""
        state["collecting_lead"] = True
        context = ""

    else:
        context = retrieve_context(last_user_message)
        system_prompt = f"""You are AutoStream's helpful AI sales assistant.
        Help the user with their query. Use the knowledge base if relevant.
        
        KNOWLEDGE BASE:
        {context}"""

    # Call Gemini
    messages_to_send = [SystemMessage(content=system_prompt)] + chat_history + [HumanMessage(content=last_user_message)]

    response = llm.invoke(messages_to_send)
    ai_response = response.content

    # Add response to state
    state["messages"].append({"role": "assistant", "content": ai_response})

    # If high intent, mark that we asked for name next
    if intent == "high_intent":
        state["last_asked"] = "name"

    return state


# ─────────────────────────────────────────────
# Node 3: Collect Lead Information
# ─────────────────────────────────────────────
def collect_lead_info(state: AgentState) -> AgentState:
    """Collect name, email, platform one by one"""

    last_user_message = state["messages"][-1]["content"].strip()
    last_asked = state.get("last_asked")

    # ── Collect Name ──
    if last_asked == "name":
        if validate_name(last_user_message):
            state["lead_name"] = last_user_message
            state["last_asked"] = "email"
            response = f"Nice to meet you, {last_user_message}! 😊 Could you share your email address so we can send you the account details?"
        else:
            response = "Could you please share your full name?"

    # ── Collect Email ──
    elif last_asked == "email":
        if validate_email(last_user_message):
            state["lead_email"] = last_user_message
            state["last_asked"] = "platform"
            response = "Perfect! 📧 And which platform do you mainly create content on? (e.g., YouTube, Instagram, TikTok, etc.)"
        else:
            response = "That doesn't look like a valid email. Could you double-check and share it again?"

    # ── Collect Platform ──
    elif last_asked == "platform":
        if validate_platform(last_user_message):
            state["lead_platform"] = last_user_message
            state["last_asked"] = "done"

            # 🎯 CALL THE LEAD CAPTURE TOOL
            result = mock_lead_capture(
                name=state["lead_name"],
                email=state["lead_email"],
                platform=last_user_message
            )

            state["lead_captured"] = True
            response = f"""🎉 You're all set, {state['lead_name']}!

Our team will reach out to you at **{state['lead_email']}** within 24 hours to get your AutoStream Pro account activated.

Welcome to the AutoStream family! 🚀 If you have any questions before then, feel free to ask!"""
        else:
            response = "Could you tell me which platform you create content on? (e.g., YouTube, Instagram, TikTok, Facebook, etc.)"

    else:
        response = "Let me help you get started! Could you share your full name?"
        state["last_asked"] = "name"

    state["messages"].append({"role": "assistant", "content": response})
    return state


# ─────────────────────────────────────────────
# Router — decides which node to go to next
# ─────────────────────────────────────────────
def router(state: AgentState) -> str:
    """Route to the correct node based on state"""

    # If already collecting lead info
    if state.get("collecting_lead") and not state.get("lead_captured"):
        if state.get("last_asked") in ["name", "email", "platform"]:
            return "collect_lead_info"

    # If lead is captured, end
    if state.get("lead_captured"):
        return END

    # Otherwise generate normal response
    return "generate_response"


# ─────────────────────────────────────────────
# Build the LangGraph
# ─────────────────────────────────────────────
def build_agent():
    """Build and compile the LangGraph agent"""

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("detect_intent", detect_intent)
    graph.add_node("generate_response", generate_response)
    graph.add_node("collect_lead_info", collect_lead_info)

    # Entry point
    graph.set_entry_point("detect_intent")

    # After detecting intent, route to correct node
    graph.add_conditional_edges(
        "detect_intent",
        router,
        {
            "generate_response": "generate_response",
            "collect_lead_info": "collect_lead_info",
            END: END
        }
    )

    # After generating response, end this turn
    graph.add_edge("generate_response", END)
    graph.add_edge("collect_lead_info", END)

    return graph.compile()


# ─────────────────────────────────────────────
# Initial State
# ─────────────────────────────────────────────
def get_initial_state() -> AgentState:
    return {
        "messages": [],
        "intent": None,
        "lead_name": None,
        "lead_email": None,
        "lead_platform": None,
        "lead_captured": False,
        "collecting_lead": False,
        "last_asked": None
    }