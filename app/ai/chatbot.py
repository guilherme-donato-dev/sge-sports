from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.repositories import ProductRepository
from app.schemas import StockAlertResponse


SYSTEM_PROMPT = """You are an intelligent assistant for a sports merchandise store called SGE Sports Store.
The store sells official merchandise for NFL, NBA, MLB, and NHL teams, including jerseys, caps, jackets, and accessories.

Your responsibilities:
- Answer questions about products, inventory, teams, and leagues
- Help staff identify low-stock items and prioritize restocking
- Provide insights about sales trends and product performance
- Answer general questions about the sports leagues and teams

Always respond in the same language as the user's question.
Be concise, professional, and helpful.
"""

STOCK_ALERT_PROMPT = """You are a stock management specialist for a sports merchandise store.

The following products are currently at or below their minimum stock threshold:

{stock_data}

Provide a concise analysis (3-5 sentences) that:
1. Highlights the most critical items needing immediate restocking
2. Groups them by league if there's a clear pattern
3. Suggests a restocking priority order

Be direct and actionable. Respond in Portuguese (Brazil).
"""


def get_llm():
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.3,
    )


async def get_chat_response(message: str) -> str:
    """Chatbot assistant for store staff."""
    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=message),
    ]
    response = await llm.ainvoke(messages)
    return response.content


async def get_stock_alert_analysis(
    low_stock_products: list[StockAlertResponse],
) -> str:
    """AI analysis of low stock products."""
    if not low_stock_products:
        return "Todos os produtos estão com estoque adequado. Nenhuma ação necessária no momento."

    stock_lines = []
    for p in low_stock_products:
        stock_lines.append(
            f"- [{p.league}] {p.name} (SKU: {p.sku}) | Time: {p.team} | "
            f"Estoque atual: {p.current_stock} | Mínimo: {p.min_stock_alert}"
        )

    stock_data = "\n".join(stock_lines)
    prompt = STOCK_ALERT_PROMPT.format(stock_data=stock_data)

    llm = get_llm()
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return response.content
