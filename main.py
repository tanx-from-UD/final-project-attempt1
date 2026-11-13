from drafter import *
from dataclasses import dataclass
from bakery import assert_equal


# --- 1. DATACLASSES ---

@dataclass
class Chemical:
    name: str
    formula: str
    coefficient: int
    molar_mass: float
    mass_grams: float
    is_reactant: bool
    notes: str


@dataclass
class State:
    equation_text: str
    chemicals: list[Chemical]
    actual_yield: float
    result_message: str


# --- 2. HELPER FUNCTIONS ---

def get_limiting_reactant(reactants: list[Chemical]) -> Chemical:
    """Finds and returns the limiting reactant based on mole ratios."""
    limiting_reactant = reactants[0]
    min_ratio = (
        (limiting_reactant.mass_grams / limiting_reactant.molar_mass)
        / limiting_reactant.coefficient
    )

    for r in reactants:
        if r.molar_mass > 0 and r.coefficient > 0:
            moles = r.mass_grams / r.molar_mass
            ratio = moles / r.coefficient
            if ratio < min_ratio:
                min_ratio = ratio
                limiting_reactant = r

    return limiting_reactant


def format_chemical_line(chem: Chemical) -> str:
    """Formats a single Chemical instance into a readable summary string."""
    role = "Reactant" if chem.is_reactant else "Product"
    return (
        f"- {chem.name} ({chem.formula}): {chem.coefficient} mol, "
        f"{chem.molar_mass} g/mol | Type: {role} | "
        f"Starting Mass: {chem.mass_grams}g"
    )


# --- 3. ROUTES & PAGES ---

@route
def index(state: State) -> Page:
    """Displays the home page to welcome the user."""
    return Page(state, [
        "Welcome to the Chemistry Stoichiometry Assistant!",
        "Calculate limiting reactants, theoretical yield, and percent yield.",
        Button("Start a calculation", reaction_input)
    ])


@route
def reaction_input(state: State) -> Page:
    """Displays the input form for the balanced chemical equation."""
    return Page(state, [
        "Enter your balanced chemical equation:",
        TextBox("equation", "e.g., 2H2 + O2 -> 2H2O"),
        Button("Save Reaction", save_reaction)
    ])


@route
def save_reaction(state: State, equation: str) -> Page:
    """Validates and saves the chemical equation to the state."""
    if not equation:
        state.result_message = "Equation cannot be empty. Please try again."
        return reaction_input(state)

    state.equation_text = equation
    return reaction_summary(state)


@route
def reaction_summary(state: State) -> Page:
    """Displays the current equation and a list of all saved chemicals."""
    content = [
        f"Current Equation: {state.equation_text}",
        "---",
        "Chemicals added so far:"
    ]

    if not state.chemicals:
        content.append("No chemicals added yet.")
    else:
        for chem in state.chemicals:
            content.append(format_chemical_line(chem))

    content.extend([
        "---",
        Button("Add Chemical (Reactant/Product)", add_chemical),
        "Enter Actual Product Yield (grams) - leave as 0.0 if unknown:",
        TextBox("actual_yield_input", "0.0"),
        Button("Calculate Results", calculate_results),
        Button("Start Over", reset)
    ])

    return Page(state, content)


@route
def add_chemical(state: State) -> Page:
    """Displays a form with SelectBox, TextBox, and TextArea for a chemical."""
    return Page(state, [
        "Add a Chemical to the Reaction",
        "Type:", SelectBox("chem_type", ["Reactant", "Product"]),
        "Name:", TextBox("name", "Water"),
        "Formula:", TextBox("formula", "H2O"),
        "Coefficient:", TextBox("coefficient", "1"),
        "Molar Mass (g/mol):", TextBox("molar_mass", "18.015"),
        "Starting Mass (g) [Enter 0 if Product]:", TextBox("mass_grams", "0.0"),
        "Additional Notes:", TextArea("notes", "State (s, l, g, aq)"),
        Button("Save Chemical", save_chemical),
        Button("Cancel", reaction_summary)
    ])


@route
def save_chemical(
    state: State,
    chem_type: str,
    name: str,
    formula: str,
    coefficient: str,
    molar_mass: str,
    mass_grams: str,
    notes: str
) -> Page:
    """Converts input strings into types and appends the Chemical to state."""
    is_reactant = True if chem_type == "Reactant" else False

    if not name or not formula:
        state.result_message = "Error: Name and formula are required."
        return reaction_summary(state)

    new_chem = Chemical(
        name=name,
        formula=formula,
        coefficient=int(coefficient),
        molar_mass=float(molar_mass),
        mass_grams=float(mass_grams),
        is_reactant=is_reactant,
        notes=notes
    )
    state.chemicals.append(new_chem)
    return reaction_summary(state)


@route
def calculate_results(state: State, actual_yield_input: str) -> Page:
    """Sorts chemicals, finds the limiting reactant, and computes yields."""
    state.actual_yield = float(actual_yield_input)

    reactants = []
    products = []

    for chem in state.chemicals:
        if chem.is_reactant:
            reactants.append(chem)
        else:
            products.append(chem)

    if not reactants or not products:
        state.result_message = (
            "Error: Need at least one reactant and one product."
        )
        return results(state)

    limiting = get_limiting_reactant(reactants)
    target_product = products[0]
    min_ratio = (
        (limiting.mass_grams / limiting.molar_mass) / limiting.coefficient
    )
    theoretical_yield = (
        min_ratio * target_product.coefficient * target_product.molar_mass
    )

    msg = f"Limiting Reactant: {limiting.name} ({limiting.formula}) | "
    msg += (
        f"Theoretical Yield of {target_product.name}: "
        f"{theoretical_yield:.2f} g"
    )

    if state.actual_yield > 0:
        percent_yield = (state.actual_yield / theoretical_yield) * 100
        msg += f" | Percent Yield: {percent_yield:.2f}%"

    state.result_message = msg
    return results(state)


@route
def results(state: State) -> Page:
    """Displays the final stoichiometry calculation results."""
    return Page(state, [
        "Calculation Results:",
        state.result_message,
        Button("View Explanation", explanation),
        Button("Start Over", reset)
    ])


@route
def explanation(state: State) -> Page:
    """Provides a step-by-step breakdown of how the stoichiometry math works."""
    return Page(state, [
        "How the Calculation Works:",
        "1. Convert starting mass to moles (mass / molar mass).",
        "2. Divide moles by the stoichiometric coefficient.",
        "3. The reactant with the smallest ratio is limiting.",
        "4. Multiply ratio by product coefficient and molar mass for Yield.",
        "5. Percent Yield = (Actual Yield / Theoretical Yield) * 100.",
        Button("Back to Results", results),
        Button("Start Over", reset)
    ])


@route
def reset(state: State) -> Page:
    """Resets all state attributes to their default starting values."""
    state.equation_text = ""
    state.chemicals = []
    state.actual_yield = 0.0
    state.result_message = ""
    return index(state)


# --- 4. SITE INFORMATION & UNIT TESTS ---

set_site_information(
    "tanx@udel.edu",
    "Chemistry Stoichiometry Assistant that calculates limiting reactants, "
    "theoretical yield, and percent yield for balanced reactions.",
    ["OpenStax Chemistry 2e (Chapter 4: Stoichiometry)"],
    [
        "Copy of CS1 Final Project 0_ Pick a Problem (1).pdf",
        "Copy of CS1 Final Project 1_ Design (1).docx"
    ],
    ["https://github.com/tanx-from-UD/final-project-attempt1"]
)

hide_debug_information()

# Global Constants for Unit Testing
H2_TEST = Chemical("Hydrogen", "H2", 2, 2.0, 2.0, True, "gas")
O2_TEST = Chemical("Oxygen", "O2", 1, 32.0, 32.0, True, "gas")
H2O_TEST = Chemical("Water", "H2O", 2, 18.0, 0.0, False, "liquid")
EXPECTED_MSG = (
    "Limiting Reactant: Hydrogen (H2) | "
    "Theoretical Yield of Water: 18.00 g | "
    "Percent Yield: 50.00%"
)

# Helper Tests
assert_equal(get_limiting_reactant([H2_TEST, O2_TEST]), H2_TEST)
assert_equal(
    format_chemical_line(H2_TEST),
    "- Hydrogen (H2): 2 mol, 2.0 g/mol | Type: Reactant | Starting Mass: 2.0g"
)

# Route 1: index
assert_equal(
    index(State("", [], 0.0, "")),
    Page(State("", [], 0.0, ""), [
        "Welcome to the Chemistry Stoichiometry Assistant!",
        "Calculate limiting reactants, theoretical yield, and percent yield.",
        Button("Start a calculation", "reaction_input")
    ])
)

# Route 2: reaction_input
assert_equal(
    reaction_input(State("", [], 0.0, "")),
    Page(State("", [], 0.0, ""), [
        "Enter your balanced chemical equation:",
        TextBox("equation", "e.g., 2H2 + O2 -> 2H2O"),
        Button("Save Reaction", "save_reaction")
    ])
)

# Route 3: save_reaction
assert_equal(
    save_reaction(State("", [], 0.0, ""), "2H2 + O2 -> 2H2O"),
    Page(State("2H2 + O2 -> 2H2O", [], 0.0, ""), [
        "Current Equation: 2H2 + O2 -> 2H2O",
        "---",
        "Chemicals added so far:",
        "No chemicals added yet.",
        "---",
        Button("Add Chemical (Reactant/Product)", "add_chemical"),
        "Enter Actual Product Yield (grams) - leave as 0.0 if unknown:",
        TextBox("actual_yield_input", "0.0"),
        Button("Calculate Results", "calculate_results"),
        Button("Start Over", "reset")
    ])
)

# Route 4: reaction_summary
assert_equal(
    reaction_summary(State("A -> B", [], 0.0, "")),
    Page(State("A -> B", [], 0.0, ""), [
        "Current Equation: A -> B",
        "---",
        "Chemicals added so far:",
        "No chemicals added yet.",
        "---",
        Button("Add Chemical (Reactant/Product)", "add_chemical"),
        "Enter Actual Product Yield (grams) - leave as 0.0 if unknown:",
        TextBox("actual_yield_input", "0.0"),
        Button("Calculate Results", "calculate_results"),
        Button("Start Over", "reset")
    ])
)

# Route 5: add_chemical
assert_equal(
    add_chemical(State("", [], 0.0, "")),
    Page(State("", [], 0.0, ""), [
        "Add a Chemical to the Reaction",
        "Type:", SelectBox("chem_type", ["Reactant", "Product"]),
        "Name:", TextBox("name", "Water"),
        "Formula:", TextBox("formula", "H2O"),
        "Coefficient:", TextBox("coefficient", "1"),
        "Molar Mass (g/mol):", TextBox("molar_mass", "18.015"),
        "Starting Mass (g) [Enter 0 if Product]:", TextBox("mass_grams", "0.0"),
        "Additional Notes:", TextArea("notes", "State (s, l, g, aq)"),
        Button("Save Chemical", "save_chemical"),
        Button("Cancel", "reaction_summary")
    ])
)

# Route 6: save_chemical
assert_equal(
    save_chemical(
        State("2H2 + O2 -> 2H2O", [], 0.0, ""),
        "Reactant", "Hydrogen", "H2", "2", "2.0", "2.0", "gas"
    ),
    Page(State("2H2 + O2 -> 2H2O", [H2_TEST], 0.0, ""), [
        "Current Equation: 2H2 + O2 -> 2H2O",
        "---",
        "Chemicals added so far:",
        "- Hydrogen (H2): 2 mol, 2.0 g/mol | Type: Reactant | Starting Mass: 2.0g",
        "---",
        Button("Add Chemical (Reactant/Product)", "add_chemical"),
        "Enter Actual Product Yield (grams) - leave as 0.0 if unknown:",
        TextBox("actual_yield_input", "0.0"),
        Button("Calculate Results", "calculate_results"),
        Button("Start Over", "reset")
    ])
)

# Route 7: calculate_results
assert_equal(
    calculate_results(
        State("2H2 + O2 -> 2H2O", [H2_TEST, O2_TEST, H2O_TEST], 0.0, ""),
        "9.0"
    ),
    Page(
        State(
            "2H2 + O2 -> 2H2O",
            [H2_TEST, O2_TEST, H2O_TEST],
            9.0,
            EXPECTED_MSG
        ),
        [
            "
