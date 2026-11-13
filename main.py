from drafter import *
from dataclasses import dataclass
from bakery import assert_equal

# --- 1. DATACLASSES ---

@dataclass
class Chemical:
    name: str
    formula: str
    coef: int
    molar_mass: float
    mass: float
    is_reactant: bool

@dataclass
class State:
    equation: str
    chemicals: list[Chemical]
    actual_yield: float
    msg: str


# --- 2. HELPER FUNCTION ---

def get_limiting(reactants):
    # Start with the first one as the baseline
    limiting = reactants[0]
    min_ratio = (limiting.mass / limiting.molar_mass) / limiting.coef

    for r in reactants:
        ratio = (r.mass / r.molar_mass) / r.coef
        if ratio < min_ratio:
            min_ratio = ratio
            limiting = r

    return limiting


# --- 3. ROUTES ---

@route
def index(state: State):
    return Page(state, [
        "Xavier's Stoichiometry Calculator",
        "Enter your balanced equation:",
        TextBox("eq", "e.g., N2 + 3H2 -> 2NH3"),
        Button("Start", save_eq)
    ])

@route
def save_eq(state: State, eq: str):
    if not eq:
        state.msg = "Equation can't be empty."
        return index(state)
    state.equation = eq
    return main_hub(state)

@route
def main_hub(state: State):
    content = [f"Equation: {state.equation}", "---", "Chemicals:"]
    
    if not state.chemicals:
        content.append("None added yet.")
    else:
        for c in state.chemicals:
            kind = "Reactant" if c.is_reactant else "Product"
            content.append(f"- {c.name} ({c.formula}) | {c.mass}g | {kind}")
            
    content.extend([
        "---",
        Button("Add Chemical", add_chem),
        "Actual yield in grams (leave 0.0 if not known):",
        TextBox("actual_y", "0.0"),
        Button("Calculate", calc_results),
        Button("Restart", reset)
    ])
    return Page(state, content)

@route
def add_chem(state: State):
    return Page(state, [
        "Type:", SelectBox("c_type", ["Reactant", "Product"]),
        "Name:", TextBox("name", "Ammonia"),
        "Formula:", TextBox("formula", "NH3"),
        "Coefficient:", TextBox("coef", "2"),
        "Molar Mass (g/mol):", TextBox("mmass", "17.031"),
        "Starting Mass (0 for products):", TextBox("mass", "0.0"),
        Button("Save", save_chem)
    ])

@route
def save_chem(state: State, c_type: str, name: str, formula: str, coef: str, mmass: str, mass: str):
    is_r = (c_type == "Reactant")
    new_chem = Chemical(name, formula, int(coef), float(mmass), float(mass), is_r)
    state.chemicals.append(new_chem)
    return main_hub(state)

@route
def calc_results(state: State, actual_y: str):
    state.actual_yield = float(actual_y)
    
    reactants = [c for c in state.chemicals if c.is_reactant]
    products = [c for c in state.chemicals if not c.is_reactant]
    
    if not reactants or not products:
        state.msg = "Need at least 1 reactant and 1 product."
        return results(state)

    lim = get_limiting(reactants)
    prod = products[0]
    
    # Calculate yield based on the limiting reactant
    moles_lim = lim.mass / lim.molar_mass
    ratio = moles_lim / lim.coef
    theo_yield = ratio * prod.coef * prod.molar_mass
    
    state.msg = f"Limiting Reactant: {lim.name} ({lim.formula}) | Theoretical Yield: {theo_yield:.2f}g"
    
    if state.actual_yield > 0:
        pct = (state.actual_yield / theo_yield) * 100
        state.msg += f" | Percent Yield: {pct:.2f}%"
        
    return results(state)

@route
def results(state: State):
    return Page(state, [
        "Results:",
        state.msg,
        Button("See Explanation", explanation),
        Button("Restart", reset)
    ])

@route
def explanation(state: State):
    return Page(state, [
        "How it works:",
        "1. Convert starting grams to moles.",
        "2. Divide by the balanced equation coefficient.",
        "3. The smallest ratio is the limiting reactant.",
        "4. Multiply that ratio by the product's coefficient and molar mass.",
        Button("Back", results)
    ])

@route
def reset(state: State):
    state.equation = ""
    state.chemicals = []
    state.actual_yield = 0.0
    state.msg = ""
    return index(state)


# --- 4. SITE INFORMATION & UNIT TESTS ---

set_site_information(
    "tanx@udel.edu",
    "Xavier's Stoichiometry Assistant",
    ["OpenStax Chemistry 2e (Chapter 4: Stoichiometry)"],
    ["Week_10_Brainstorming.pdf", "Week_11_Design_Phase.docx"],
    ["https://github.com/tanx-from-UD/final-project-attempt1"]
)

hide_debug_information()

# Test Data
H2_TEST = Chemical("Hydrogen", "H2", 2, 2.0, 2.0, True)
O2_TEST = Chemical("Oxygen", "O2", 1, 32.0, 32.0, True)
H2O_TEST = Chemical("Water", "H2O", 2, 18.0, 0.0, False)
EXPECTED_MSG = "Limiting Reactant: Hydrogen (H2) | Theoretical Yield: 18.00g | Percent Yield: 50.00%"

# Helper Tests
assert_equal(get_limiting([H2_TEST, O2_TEST]), H2_TEST)

# Route Tests
assert_equal(
    index(State("", [], 0.0, "")),
    Page(State("", [], 0.0, ""), [
        "Xavier's Stoichiometry Calculator",
        "Enter your balanced equation:",
        TextBox("eq", "e.g., N2 + 3H2 -> 2NH3"),
        Button("Start", "save_eq")
    ])
)

assert_equal(
    save_eq(State("", [], 0.0, ""), "2H2 + O2 -> 2H2O"),
    Page(State("2H2 + O2 -> 2H2O", [], 0.0, ""), [
        "Equation: 2H2 + O2 -> 2H2O", "---", "Chemicals:",
        "None added yet.", "---",
        Button("Add Chemical", "add_chem"),
        "Actual yield in grams (leave 0.0 if not known):",
        TextBox("actual_y", "0.0"),
        Button("Calculate", "calc_results"),
        Button("Restart", "reset")
    ])
)

assert_equal(
    main_hub(State("A -> B", [], 0.0, "")),
    Page(State("A -> B", [], 0.0, ""), [
        "Equation: A -> B", "---", "Chemicals:",
        "None added yet.", "---",
        Button("Add Chemical", "add_chem"),
        "Actual yield in grams (leave 0.0 if not known):",
        TextBox("actual_y", "0.0"),
        Button("Calculate", "calc_results"),
        Button("Restart", "reset")
    ])
)

assert_equal(
    add_chem(State("", [], 0.0, "")),
    Page(State("", [], 0.0, ""), [
        "Type:", SelectBox("c_type", ["Reactant", "Product"]),
        "Name:", TextBox("name", "Ammonia"),
        "Formula:", TextBox("formula", "NH3"),
        "Coefficient:", TextBox("coef", "2"),
        "Molar Mass (g/mol):", TextBox("mmass", "17.031"),
        "Starting Mass (0 for products):", TextBox("mass", "0.0"),
        Button("Save", "save_chem")
    ])
)

assert_equal(
    save_chem(State("2H2 + O2 -> 2H2O", [], 0.0, ""), "Reactant", "Hydrogen", "H2", "2", "2.0", "2.0"),
    Page(State("2H2 + O2 -> 2H2O", [H2_TEST], 0.0, ""), [
        "Equation: 2H2 + O2 -> 2H2O", "---", "Chemicals:",
        "- Hydrogen (H2) | 2.0g | Reactant", "---",
        Button("Add Chemical", "add_chem"),
        "Actual yield in grams (leave 0.0 if not known):",
        TextBox("actual_y", "0.0"),
        Button("Calculate", "calc_results"),
        Button("Restart", "reset")
    ])
)

assert_equal(
    calc_results(State("2H2 + O2 -> 2H2O", [H2_TEST, O2_TEST, H2O_TEST], 0.0, ""), "9.0"),
    Page(State("2H2 + O2 -> 2H2O", [H2_TEST, O2_TEST, H2O_TEST], 9.0, EXPECTED_MSG), [
        "Results:", EXPECTED_MSG,
        Button("See Explanation", "explanation"),
        Button("Restart", "reset")
    ])
)

assert_equal(
    results(State("", [], 0.0, "Test Msg")),
    Page(State("", [], 0.0, "Test Msg"), [
        "Results:", "Test Msg",
        Button("See Explanation", "explanation"),
        Button("Restart", "reset")
    ])
)

assert_equal(
    explanation(State("", [], 0.0, "")),
    Page(State("", [], 0.0, ""), [
        "How it works:",
        "1. Convert starting grams to moles.",
        "2. Divide by the balanced equation coefficient.",
        "3. The smallest ratio is the limiting reactant.",
        "4. Multiply that ratio by the product's coefficient and molar mass.",
        Button("Back", "results")
    ])
)

assert_equal(
    reset(State("A -> B", [H2_TEST], 5.0, "Done")),
    Page(State("", [], 0.0, ""), [
        "Xavier's Stoichiometry Calculator",
        "Enter your balanced equation:",
        TextBox("eq", "e.g., N2 + 3H2 -> 2NH3"),
        Button("Start", "save_eq")
    ])
)

start_server(State("", [], 0.0, ""))
