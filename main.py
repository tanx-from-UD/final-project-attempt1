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
            "Calculation Results:",
            EXPECTED_MSG,
            Button("View Explanation", "explanation"),
            Button("Start Over", "reset")
        ]
    )
)

# Route 8: results
assert_equal(
    results(State("", [], 0.0, "Test Result")),
    Page(State("", [], 0.0, "Test Result"), [
        "Calculation Results:",
        "Test Result",
        Button("View Explanation", "explanation"),
        Button("Start Over", "reset")
    ])
)

# Route 9: explanation
assert_equal(
    explanation(State("", [], 0.0, "")),
    Page(State("", [], 0.0, ""), [
        "How the Calculation Works:",
        "1. Convert starting mass to moles (mass / molar mass).",
        "2. Divide moles by the stoichiometric coefficient.",
        "3. The reactant with the smallest ratio is limiting.",
        "4. Multiply ratio by product coefficient and molar mass for Yield.",
        "5. Percent Yield = (Actual Yield / Theoretical Yield) * 100.",
        Button("Back to Results", "results"),
        Button("Start Over", "reset")
    ])
)

# Route 10: reset
assert_equal(
    reset(State("2H2 + O2 -> 2H2O", [H2_TEST], 5.0, "Done")),
    Page(State("", [], 0.0, ""), [
        "Welcome to the Chemistry Stoichiometry Assistant!",
        "Calculate limiting reactants, theoretical yield, and percent yield.",
        Button("Start a calculation", "reaction_input")
    ])
)

start_server(State("", [], 0.0, ""))
