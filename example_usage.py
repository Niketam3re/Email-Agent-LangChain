"""
Example usage of the Email AI Agent
Demonstrates both initial scan and continuous draft generation
"""

import asyncio
from agent import create_email_agent
from langchain_core.messages import HumanMessage


async def example_initial_scan():
    """
    Example: Perform initial inbox scan
    This will analyze your entire Gmail inbox and learn patterns
    """
    print("=" * 80)
    print("EXAMPLE 1: Initial Inbox Scan")
    print("=" * 80)

    # Create the agent
    agent = await create_email_agent()

    # Prepare the request
    request = {
        "messages": [
            HumanMessage(content="""
                Please perform an initial scan of my Gmail inbox:

                1. Scan all my emails (or last 1000 for testing)
                2. Identify different categories and subcategories
                3. Classify all emails into these categories
                4. Analyze communication patterns for each category
                5. Generate response drafting rules
                6. Create a Mermaid diagram showing my inbox structure

                Please be thorough and use the write_todos tool to plan your work.
            """)
        ]
    }

    print("\n📧 Starting inbox scan...")
    print("This may take a few minutes for large inboxes.\n")

    # Invoke the agent
    result = agent.invoke(request)

    # Display the result
    print("\n" + "=" * 80)
    print("AGENT RESPONSE:")
    print("=" * 80)
    final_message = result["messages"][-1]
    print(final_message.content)
    print("=" * 80)


async def example_draft_response():
    """
    Example: Generate a draft response for a new email
    This should be run after the initial scan is complete
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Generate Draft Response")
    print("=" * 80)

    # Create the agent
    agent = await create_email_agent()

    # Prepare the request
    request = {
        "messages": [
            HumanMessage(content="""
                I received a new email with the following details:

                From: john.smith@company.com
                Subject: Q4 Project Alpha Status Update Required
                Body:
                Hi there,

                Can you please send me a status update on Project Alpha?
                We need to review progress before the Q4 planning meeting next week.

                The board is particularly interested in:
                - Current milestone completion percentage
                - Any blockers or risks
                - Projected completion date

                Thanks,
                John

                ---

                Please:
                1. Classify this email into the appropriate category
                2. Generate a contextually appropriate draft response
                3. Explain why you chose this response style
            """)
        ]
    }

    print("\n✍️ Generating draft response...")
    print()

    # Invoke the agent
    result = agent.invoke(request)

    # Display the result
    print("\n" + "=" * 80)
    print("AGENT RESPONSE:")
    print("=" * 80)
    final_message = result["messages"][-1]
    print(final_message.content)
    print("=" * 80)


async def example_category_analysis():
    """
    Example: Analyze a specific category
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Analyze Specific Category")
    print("=" * 80)

    # Create the agent
    agent = await create_email_agent()

    # Prepare the request
    request = {
        "messages": [
            HumanMessage(content="""
                Please analyze the "Work" category from my inbox:

                1. How many emails are in this category?
                2. What are the communication patterns?
                3. What response rules have been learned?
                4. Show me example phrases commonly used
                5. What's the typical response tone and formality?

                Retrieve this information from Supabase using your database tools.
            """)
        ]
    }

    print("\n🔍 Analyzing category...")
    print()

    # Invoke the agent
    result = agent.invoke(request)

    # Display the result
    print("\n" + "=" * 80)
    print("AGENT RESPONSE:")
    print("=" * 80)
    final_message = result["messages"][-1]
    print(final_message.content)
    print("=" * 80)


async def example_update_rules():
    """
    Example: Update response rules for a category
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Update Response Rules")
    print("=" * 80)

    # Create the agent
    agent = await create_email_agent()

    # Prepare the request
    request = {
        "messages": [
            HumanMessage(content="""
                I'd like to update the response rules for the "Hockey > Team A" category.

                Please update the rules to:
                - Use a more casual tone
                - Keep responses very brief (1-2 sentences max)
                - Always include "Go team!" at the end
                - Use phrases like "Sounds good!" and "See you there!"

                Update these rules in Supabase so future drafts follow this style.
            """)
        ]
    }

    print("\n⚙️ Updating rules...")
    print()

    # Invoke the agent
    result = agent.invoke(request)

    # Display the result
    print("\n" + "=" * 80)
    print("AGENT RESPONSE:")
    print("=" * 80)
    final_message = result["messages"][-1]
    print(final_message.content)
    print("=" * 80)


async def main():
    """
    Main function - run examples based on user choice
    """
    print("\n" + "=" * 80)
    print("Email AI Agent - Example Usage")
    print("=" * 80)
    print("\nAvailable examples:")
    print("1. Initial Inbox Scan (run this first)")
    print("2. Generate Draft Response (requires initial scan)")
    print("3. Analyze Specific Category (requires initial scan)")
    print("4. Update Response Rules (requires initial scan)")
    print("5. Run all examples")
    print("0. Exit")

    choice = input("\nSelect an example (0-5): ").strip()

    if choice == "1":
        await example_initial_scan()
    elif choice == "2":
        await example_draft_response()
    elif choice == "3":
        await example_category_analysis()
    elif choice == "4":
        await example_update_rules()
    elif choice == "5":
        print("\n🚀 Running all examples...")
        await example_initial_scan()
        await asyncio.sleep(2)
        await example_draft_response()
        await asyncio.sleep(2)
        await example_category_analysis()
        await asyncio.sleep(2)
        await example_update_rules()
    elif choice == "0":
        print("Goodbye!")
        return
    else:
        print("Invalid choice. Please select 0-5.")
        await main()

    print("\n✅ Example completed!")
    print("\n💡 Tip: Check LangSmith for detailed execution traces")
    print("   URL: https://smith.langchain.com/")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your .env file has all required credentials")
        print("   2. Ensure Supabase schema is set up")
        print("   3. Verify Gmail MCP server is configured")
        print("   4. Run: python setup.py to verify setup")
