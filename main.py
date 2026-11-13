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

# Finds and returns the limiting reactant based on mole ratios
def get_limiting_reactant(reactants: list[Chemical]) -> Chemical:
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


# Formats a single Chemical instance into a readable summary string
def format_chemical_line(chem: Chemical) -> str:
    role = "Reactant" if chem.is_reactant else "Product"
    return (
        f"- {chem.name} ({chem.formula}) | {chem.coefficient} moles, "
        f"{chem.molar_mass} g/mol | {role} | Starting amount: {chem.mass_grams}g"
    )


# --- 3. ROUTES & PAGES ---

@route
def index(state: State) -> Page:
    # Show the main welcome page
    return Page(state, [
        "Welcome to Xavier's Stoichiometry Calculator!",
        "Let's figure out limiting reactants, theoretical yields, and percent yields.",
        Button("Let's get started", reaction_input)
    ])


@route
def reaction_input(state: State) -> Page:
    # Ask the user for the chemical equation
    return Page(state, [
        "What is your balanced equation?",
        TextBox("equation", "e.g., N2 + 3H2 -> 2NH3"),
        Button("Lock it in", save_reaction)
    ])


@route
def save_reaction(state: State, equation: str) -> Page:
    # Check if equation is empty and save it
    if not equation:
        state.result_message = "You can't leave the equation blank! Try again."
        return reaction_input(state)

    state.equation_text = equation
    return reaction_summary(state)


@route
def reaction_summary(state: State) -> Page:
    # Show equation and current list of chemicals
    content = [
        f"Working with: {state.equation_text}",
        "---",
        "Currently added chemicals:"
    ]

    if not state.chemicals:
        content.append("Nothing added yet.")
    else:
        for chem in state.chemicals:
            content.append(format_chemical_line(chem))

    content.extend([
        "---",
        Button("Add another chemical (Reactant or Product)", add_chemical),
        "Did you run this in a lab? Enter actual yield in grams (leave 0.0 if not):",
        TextBox("actual_yield_input", "0.0"),
        Button("Run the Numbers", calculate_results),
        Button("Restart", reset)
    ])

    return Page(state, content)


@route
def add_chemical(state: State) -> Page:
    # Form to add a new chemical
    return Page(state, [
        "Fill out the chemical details below",
        "Reactant or Product?", SelectBox("chem_type", ["Reactant", "Product"]),
        "Name:", TextBox("name", "Ammonia"),
        "Formula:", TextBox("formula", "NH3"),
        "Mole Coefficient:", TextBox("coefficient", "2"),
        "Molar Mass (g/mol):", TextBox("molar_mass", "17.031"),
        "Starting Mass (g) [0 if it's a Product]:", TextBox("mass_grams", "0.0"),
        "Notes:", TextArea("notes", "Gas phase"),
        Button("Add to List", save_chemical),
        Button("Go Back", reaction_summary)
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
    # Convert types and add to state
    is_reactant = True if chem_type == "Reactant" else False

    if not name or not formula:
        state.result_message = "Hold on, you need to provide a name and formula."
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
    # Do the actual stoichiometry math
    state.actual_yield = float(actual_yield_input)

    reactants = []
    products = []

    for chem in state.chemicals:
        if chem.is_reactant:
            reactants.append(chem)
        else:
            products.append(chem)

    if not reactants or not products:
        state.result
