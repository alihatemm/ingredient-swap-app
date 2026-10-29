"""
Ingredient Replacement Logic.

A simple dictionary that maps a common (less healthy) ingredient to a
healthier alternative and a short reason. Keys are lowercase.

To add a new swap, just add a new entry to REPLACEMENTS.
"""

REPLACEMENTS = {
    "sugar": {
        "replacement": "honey or maple syrup (in moderation)",
        "reason": "Less refined and sweeter, so you can use less.",
    },
    "high fructose corn syrup": {
        "replacement": "pure maple syrup or fruit puree",
        "reason": "Avoids a highly processed sweetener linked to excess calorie intake.",
    },
    "corn syrup": {
        "replacement": "honey or fruit puree",
        "reason": "Less processed source of sweetness.",
    },
    "white flour": {
        "replacement": "whole wheat flour",
        "reason": "More fiber, vitamins and minerals.",
    },
    "enriched flour": {
        "replacement": "whole wheat flour",
        "reason": "Whole grains keep the fiber that refining removes.",
    },
    "bleached flour": {
        "replacement": "whole wheat flour",
        "reason": "Whole grains keep the fiber that refining removes.",
    },
    "wheat flour": {
        "replacement": "whole wheat flour",
        "reason": "Whole grains keep the fiber that refining removes.",
    },
    "palm oil": {
        "replacement": "olive oil",
        "reason": "Less saturated fat and more heart-healthy fats.",
    },
    "hydrogenated oil": {
        "replacement": "olive oil or avocado oil",
        "reason": "Avoids trans fats.",
    },
    "partially hydrogenated oil": {
        "replacement": "olive oil or avocado oil",
        "reason": "Avoids trans fats.",
    },
    "vegetable oil": {
        "replacement": "olive oil",
        "reason": "Higher in monounsaturated fats.",
    },
    "shortening": {
        "replacement": "olive oil or unsweetened applesauce",
        "reason": "Cuts saturated and trans fats.",
    },
    "butter": {
        "replacement": "olive oil or avocado",
        "reason": "Less saturated fat.",
    },
    "margarine": {
        "replacement": "olive oil",
        "reason": "Avoids processed fats.",
    },
    "salt": {
        "replacement": "herbs and spices or low-sodium salt",
        "reason": "Lowers sodium intake.",
    },
    "sodium": {
        "replacement": "herbs and spices",
        "reason": "Lowers sodium intake.",
    },
    "white rice": {
        "replacement": "brown rice or quinoa",
        "reason": "More fiber and protein.",
    },
    "milk chocolate": {
        "replacement": "dark chocolate (70%+ cocoa)",
        "reason": "Less sugar and more antioxidants.",
    },
    "cream": {
        "replacement": "Greek yogurt",
        "reason": "Less fat and more protein.",
    },
    "sour cream": {
        "replacement": "plain Greek yogurt",
        "reason": "Less fat and more protein.",
    },
    "mayonnaise": {
        "replacement": "Greek yogurt or mashed avocado",
        "reason": "Less fat, more nutrients.",
    },
    "artificial flavors": {
        "replacement": "natural spices, vanilla or citrus zest",
        "reason": "Avoids synthetic additives.",
    },
    "artificial flavor": {
        "replacement": "natural spices, vanilla or citrus zest",
        "reason": "Avoids synthetic additives.",
    },
    "monosodium glutamate": {
        "replacement": "herbs, garlic or onion powder",
        "reason": "Flavor without added sodium.",
    },
    "msg": {
        "replacement": "herbs, garlic or onion powder",
        "reason": "Flavor without added sodium.",
    },
    "aspartame": {
        "replacement": "stevia or monk fruit",
        "reason": "Plant-based sweetener alternative.",
    },
    "sucralose": {
        "replacement": "stevia or monk fruit",
        "reason": "Plant-based sweetener alternative.",
    },
    "dextrose": {
        "replacement": "fruit puree",
        "reason": "Natural sweetness with fiber.",
    },
}


def find_replacements(ingredients):
    """
    For each ingredient, look for a matching key in REPLACEMENTS.

    Matching is done on whole words, preferring the longest key, so
    "high fructose corn syrup" matches that entry instead of plain "corn syrup",
    and "sugar" will match "cane sugar" but "salt" won't match "unsalted".
    """
    suggestions = []
    # Longest keys first so the most specific match wins.
    keys = sorted(REPLACEMENTS.keys(), key=len, reverse=True)

    for ingredient in ingredients:
        padded = f" {ingredient.lower()} "
        for key in keys:
            if f" {key} " in padded:
                suggestions.append(
                    {
                        "original": ingredient,
                        "matched": key,
                        "replacement": REPLACEMENTS[key]["replacement"],
                        "reason": REPLACEMENTS[key]["reason"],
                    }
                )
                break  # one suggestion per ingredient

    return suggestions
