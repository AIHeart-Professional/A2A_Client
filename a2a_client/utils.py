

async def get_card_descriptions(cards: list) -> str:
    """Extracts and formats the descriptions from a list of agent cards."""
    descriptions = []
    for card in cards:
        description = card.get("description", "")
        if description:
            descriptions.append(description)
    return "\n".join(descriptions)
