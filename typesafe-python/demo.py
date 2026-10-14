import os

from main import JevLib


def run_feel(jl: JevLib) -> None:
    email_state = """
    Please resolve my email immediately!
    """

    if jl.feels(email_state, "needs an urgent reply") > 0.7:
        print("The email needs an urgent reply.")
    else:
        print("The email does not need an urgent reply.")


def run_feel_llm() -> None:
    email_state = "Please resolve my email immediately!"
    reply = JevLib.llm(
        "Draft a calm, helpful reply in one short sentence.",
        using=email_state,
        api_token=os.environ["CF_GATEWAY_API_KEY"],
    )
    print(f"Email: {email_state}")
    print(f"Draft reply: {reply}")


def run_match(jl: JevLib) -> str:
    state = "My shoes arrived in the wrong size. Can I swap them for a different size?"
    instructions = "Which team should handle this?"

    teams = {
        "Returns Team": "Exchanges, wrong or damaged items",
        "Shipping Team": "Delivery status, delays, lost packages",
        "Billing Team": "Charges, invoices, payment problems",
    }

    team = jl.match(state, instructions, teams)

    print(state)
    print(f"Route to: {team}")
    return team


def main() -> None:
    try:
        run_feel_llm()

        with JevLib(api_key="TYPESAFE_API_KEY") as jl:
            run_feel(jl)

            print("----------------------------")

            run_match(jl)
    except RuntimeError as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
