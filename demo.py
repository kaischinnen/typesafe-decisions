from typesafe_decisions import DecisionClient, llm


def run_feel(decisions: DecisionClient) -> None:
    email_state = """
    Please resolve my email immediately!
    """

    if decisions.feels(email_state, "needs an urgent reply") > 0.7:
        print("The email needs an urgent reply.")
    else:
        print("The email does not need an urgent reply.")


def run_feel_llm() -> None:
    email_state = "Please resolve my email immediately!"
    instruction = "Draft a calm, helpful reply in one short sentence."
    reply = llm(instruction, using=email_state)
    print(f"Email: {email_state}")
    print(f"Draft reply: {reply}")


def run_match(decisions: DecisionClient) -> str:
    state = "My shoes arrived in the wrong size. Can I swap them for a different size?"
    instructions = "Which team should handle this?"

    teams = {
        "Returns Team": "Exchanges, wrong or damaged items",
        "Shipping Team": "Delivery status, delays, lost packages",
        "Billing Team": "Charges, invoices, payment problems",
    }

    team = decisions.match(state, instructions, teams)

    print(state)
    print(f"Route to: {team}")
    return team


def main() -> None:
    try:
        run_feel_llm()

        with DecisionClient(api_key_env="TYPESAFE_API_KEY") as decisions:
            run_feel(decisions)

            print("----------------------------")

            run_match(decisions)
    except RuntimeError as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
