import json
import os

def load_knowledge_base():
    """Load the knowledge base from JSON file"""
    kb_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base', 'autostream_kb.json')
    with open(kb_path, 'r') as f:
        return json.load(f)


def retrieve_context(query: str) -> str:
    """
    Retrieve relevant information from knowledge base
    based on user query keywords
    """
    kb = load_knowledge_base()
    query_lower = query.lower()
    context_parts = []

    # Check for pricing/plan related queries
    if any(word in query_lower for word in ["price", "plan", "cost", "how much", "pricing", "basic", "pro", "subscription", "pay", "cheap", "expensive"]):
        context_parts.append("=== AutoStream Plans & Pricing ===")
        for plan in kb["plans"]:
            features_list = ", ".join(plan["features"])
            context_parts.append(f"{plan['name']}: {plan['price']} | Features: {features_list}")

    # Check for feature related queries
    if any(word in query_lower for word in ["feature", "4k", "caption", "resolution", "video", "editing", "tools", "unlimited"]):
        context_parts.append("=== AutoStream Features ===")
        for plan in kb["plans"]:
            features_list = ", ".join(plan["features"])
            context_parts.append(f"{plan['name']}: {features_list}")

    # Check for policy related queries
    if any(word in query_lower for word in ["refund", "cancel", "money back", "return", "policy"]):
        context_parts.append("=== Refund Policy ===")
        context_parts.append(kb["policies"]["refund"])
        context_parts.append(kb["policies"]["billing"])

    # Check for support related queries
    if any(word in query_lower for word in ["support", "help", "contact", "24/7", "customer"]):
        context_parts.append("=== Support Policy ===")
        context_parts.append(kb["policies"]["support"])

    # Check for company related queries
    if any(word in query_lower for word in ["what is", "about", "autostream", "company", "who"]):
        context_parts.append("=== About AutoStream ===")
        context_parts.append(kb["company"]["description"])

    
    if not context_parts:
        context_parts.append("=== AutoStream Complete Information ===")
        for plan in kb["plans"]:
            features_list = ", ".join(plan["features"])
            context_parts.append(f"{plan['name']}: {plan['price']} | {features_list}")
        for key, value in kb["policies"].items():
            context_parts.append(f"{key.capitalize()}: {value}")

    return "\n".join(context_parts)
