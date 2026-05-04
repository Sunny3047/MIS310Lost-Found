# anthropic_service.py
# This file uses Anthropic's Claude API to match lost items with found items

import json
from Configurations import ANTHROPIC_API_KEY

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Anthropic library not installed. Run: pip install anthropic")


def find_matches(lost_report, found_reports):
    """
    Uses Claude to analyze a lost item report against all found items
    and return ranked matches with scores and reasoning.

    Args:
        lost_report: Dict containing the lost item details
        found_reports: List of dicts containing found item details

    Returns:
        List of found reports with added match_score and match_reason fields,
        sorted by match score (highest first)
    """
    if not ANTHROPIC_AVAILABLE:
        return []

    if ANTHROPIC_API_KEY == "YOUR_ANTHROPIC_API_KEY":
        print("Please set your Anthropic API key in Configurations.py")
        return []

    # Build the prompt for Claude
    lost_desc = f"""
Lost Item:
- Name: {lost_report['item_name']}
- Category: {lost_report['category']}
- Description: {lost_report.get('description', 'N/A')}
- Location: {lost_report['location']}
- Date: {lost_report['date']}
"""

    found_list = "\n\n".join([
        f"""Found Item #{i + 1} (ID: {r['id']}):
- Name: {r['item_name']}
- Category: {r['category']}
- Description: {r.get('description', 'N/A')}
- Location: {r['location']}
- Date: {r['date']}"""
        for i, r in enumerate(found_reports)
    ])

    prompt = f"""{lost_desc}

Found Items in Database:
{found_list}

Analyze each found item and determine how likely it is to match the lost item. 
For each found item, provide:
1. A match score from 0-100 (100 = definite match, 0 = no match)
2. A brief reason for the score (one sentence)

Return your response as a JSON array with this exact format:
[
  {{"id": 1, "match_score": 85, "match_reason": "Same category and location, similar description"}},
  {{"id": 2, "match_score": 20, "match_reason": "Different category and location"}}
]

Sort the results by match_score from highest to lowest.
Only return the JSON array, no other text."""

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the text from Claude's response
        response_text = response.content[0].text.strip()

        # Parse the JSON response
        matches_data = json.loads(response_text)

        # Merge the scores back with the full report data
        results = []
        for match in matches_data:
            match_id = match["id"]
            # Find the corresponding found report
            found_report = next((r for r in found_reports if r["id"] == match_id), None)
            if found_report:
                # Add the AI scoring to the report
                found_report["match_score"] = match["match_score"]
                found_report["match_reason"] = match["match_reason"]
                results.append(found_report)

        return results

    except json.JSONDecodeError as e:
        print(f"Error parsing Claude response: {e}")
        print(f"Response was: {response_text}")
        return []
    except Exception as e:
        print(f"Error calling Anthropic API: {e}")
        return []