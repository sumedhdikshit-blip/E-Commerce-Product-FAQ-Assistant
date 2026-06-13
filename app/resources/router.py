from semantic_router import Route, SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

faq_route = Route(
    name="faq",
    utterances=[
        # --- Returns ---
        "What is your return policy?",
        "How do I return a product?",
        "How do I send back an item?",
        "What is the process for returning something?",
        "Can I return a product I bought last week?",
        "I want to return my order",
        "How do I initiate a return?",
        "What items are not eligible for return?",
        "Can I return a used product?",
        "I received the wrong item, how do I return it?",
        "What should I do if my product is defective?",
        "How do I return a damaged item?",
        "My product stopped working, can I return it?",
        "I want to exchange my product for a different size",
        "Can I exchange my order for another item?",
        "What is the exchange process?",
        "Is there a return window after delivery?",
        "How many days do I have to return a product?",

        # --- Refunds ---
        "How long does your refund take?",
        "When will I get my refund?",
        "How long does a refund take?",
        "When will my money be returned?",
        "What is the refund timeline?",
        "How many days for refund to process?",
        "I haven't received my refund yet",
        "My refund is delayed, what should I do?",
        "Where is my refund?",
        "How do I check my refund status?",
        "Will I get a full refund?",
        "Can I get a refund on a sale item?",
        "Refund not credited to my account",
        "How long does it take to get money back?",
        "When does the refund hit my bank account?",

        # --- Payments ---
        "What payment methods are accepted?",
        "Can I pay using UPI?",
        "Do you accept UPI payments?",
        "Is UPI available at checkout?",
        "Can I pay with Google Pay?",
        "Do you accept PhonePe?",
        "Which cards do you accept?",
        "Can I pay with a credit card?",
        "Do you accept debit cards?",
        "Is net banking available?",
        "Do you accept cash on delivery?",
        "Is COD available in my area?",
        "Can I pay in installments?",
        "Are there EMI options available?",
        "How do I apply a promo code?",
        "Where do I enter my coupon code?",
        "My promo code is not working",
        "Is there a discount for HDFC credit card users?",
        "Are there any active offers or coupons?",
        "How do I use my wallet balance?",
        "Can I split payment between card and wallet?",

        # --- Order Tracking & Management ---
        "How can I track my order?",
        "Where is my order?",
        "What is the status of my order?",
        "My order has not arrived yet",
        "When will my order be delivered?",
        "My package is late",
        "How do I find my tracking number?",
        "The tracking link is not working",
        "How do I cancel my order?",
        "Can I cancel after placing the order?",
        "Can I modify my order after placing it?",
        "I placed the wrong order, can I change it?",
        "How do I change the delivery address?",
        "Can I change my order before it ships?",

        # --- Shipping ---
        "How long does delivery take?",
        "What are the estimated delivery times?",
        "Do you offer express delivery?",
        "Is same-day delivery available?",
        "What are the shipping charges?",
        "Is there free shipping?",
        "Do you offer free delivery above a certain amount?",
        "Do you ship internationally?",
        "Do you deliver outside India?",
        "Which courier service do you use?",
        "Can I schedule a delivery time?",
        "What happens if I miss the delivery?",

        # --- Account & Support ---
        "How do I contact customer support?",
        "What is the customer care number?",
        "I want to speak to an agent",
        "How do I raise a complaint?",
        "How do I update my delivery address?",
        "How do I change my phone number?",
        "How do I delete my account?",
        "How do I reset my password?",
        "I can't log in to my account",
        "How do I update my email address?",
    ]
)

sql_route = Route(
    name="sql",
    utterances=[
        # --- Brand-only queries ---
        "Lenovo",
        "Samsung",
        "Abros",
        "Apple",
        "Nike",
        "Adidas",
        "HP",
        "Dell",
        "OnePlus",
        "boAt",
        "Realme",
        "Xiaomi",
        "show me Lenovo",
        "show me Samsung",
        "show me Apple products",
        "I want Nike shoes",
        "show boAt products",

        # --- Browse / Catalog ---
        "Show all products",
        "List all available items",
        "Show me the product catalog",
        "What products do you sell?",
        "Browse all items",
        "Show me everything you have",
        "What is available in your store?",
        "Show me your full inventory",

        # --- Category queries ---
        "List mobile phones",
        "Show me laptops",
        "What electronics do you have?",
        "Show all products in the clothing category",
        "Show me headphones",
        "I want to see smartwatches",
        "Show me running shoes",
        "List all tablets",
        "Show me gaming accessories",
        "What cameras do you have?",
        "Show me kitchen appliances",
        "List all men's clothing",
        "Show me women's footwear",
        "What furniture is available?",
        "Show me all TVs",
        "List refrigerators",
        "Show me air conditioners",
        "What audio products do you have?",

        # --- Price / Budget / Filter queries ---
        "Find products under 5000 rupees",
        "Show items between 1000 and 3000 rupees",
        "What are the cheapest products available?",
        "Show laptops under 40000 rupees",
        "Find phones under 15000",
        "Show me budget headphones",
        "What can I buy under 500 rupees?",
        "Show me items below 2000",
        "Find affordable options",
        "List products in the 10000 to 20000 price range",
        "What is the most expensive item you sell?",
        "Show me premium products",
        "Find the lowest price laptop",
        "What is the price range for TVs?",

        # --- Brand + Category queries ---
        "Show me Samsung phones",
        "List Samsung products",
        "Show me all Lenovo laptops",
        "Find HP printers",
        "Show me Nike running shoes",
        "List Adidas products",
        "Show Apple iPhones",
        "Find boAt earphones",
        "Show OnePlus mobiles",
        "List Dell desktops",

        # --- Rating queries ---
        "Show top rated items",
        "Which products have more than 4 star rating?",
        "List best reviewed products",
        "Show me highly rated laptops",
        "What are the top rated phones?",
        "Find products with 5 star reviews",
        "Show me products rated above 4.5",
        "Which headphones have the best reviews?",

        # --- Stock / Availability queries ---
        "Which products are in stock?",
        "Show in-stock items only",
        "Are any laptops available right now?",
        "What is currently available?",
        "Show me out of stock items",
        "Is the iPhone 15 available?",

        # --- Sales / Deals / Discounts ---
        "Are there any products on sale right now?",
        "Show me the best selling items",
        "What are today's deals?",
        "Show discounted products",
        "List items on offer",
        "Show me products with the highest discount",
        "What products have a sale?",
        "Find clearance items",
        "Show me flash sale products",
        "What are the trending products?",

        # --- Sorting / Comparison ---
        "Sort products by price low to high",
        "Show cheapest laptops first",
        "Compare Samsung and Apple phones",
        "Which is better, OnePlus or Realme?",
        "Show newest arrivals",
        "List recently added products",
    ]
)

# ---------------------------------------------------------------------------
# Router setup
# ---------------------------------------------------------------------------

print("Loading encoder...")
encoder = HuggingFaceEncoder()

print("Creating router...")
router = SemanticRouter(
    routes=[faq_route, sql_route],
    encoder=encoder,
    auto_sync="local"  # persists routes locally, no remote sync needed
)
print("Router ready.\n")


# ---------------------------------------------------------------------------
# Public function to use in your main app
# ---------------------------------------------------------------------------

def get_route(query: str) -> str | None:
    """
    Returns the route name ('faq', 'sql') for a given query.
    Returns None if no route matches confidently.
    """
    result = router(query)
    return result.name  # will be None if below confidence threshold


if __name__ == "__main__":
    test_queries = [
        # FAQ — previously failing
        "How long does your refund take?",
        "What payment methods are accepted?",
        "When will I get my refund?",
        "Can I pay using UPI?",
        # SQL — brand-only, previously failing
        "Lenovo",
        "Samsung",
        "Abros",
        # Original test suite
        "What is the return policy?",
        "How long does a refund take?",
        "Show me laptops under 40000 rupees",
        "List all Samsung phones",
        "Do you accept UPI payments?",
        "Which products are in stock?",
        "Tell me a joke",            # should return None (no route)
        "What's the weather today",  # should return None (no route)
    ]

    for query in test_queries:
        route_name = get_route(query)
        label = route_name if route_name else "❓ No route matched (fallback to LLM)"
        print(f"  Query : {query}")
        print(f"  Route : {label}\n")