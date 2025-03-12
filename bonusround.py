import pandas as pd
import streamlit as st
import numpy as np

from fuzzywuzzy import process

# read data files
allergen_data = pd.read_csv('allergen.csv')

# processing allergen synonym data
allergen_synonyms = {}
for _, row in allergen_data.iterrows():
    Common_name = row[0].strip().lower()
    synonyms = [str(s).strip().lower() for s in row[1:] if pd.notna(s)]
    allergen_synonyms[Common_name] = [Common_name] + synonyms

# streamlit UI
st.title("🍽️ Food Allergen Detection 🥜🚨")

# function to input known allergens
def get_allergens():
    user_allergens = st.text_input("Enter a list of your allergies, seperated by commas (e.g. peanut, dairy, soy): ")
    return [allergen.strip().lower() for allergen in user_allergens.split(",")]

# function to input food product ingredients
def get_ingredients():
    ingredients = st.text_input("Enter the ingredients of the food product you'd like to check, separated by commas (e.g. milk, eggs, flour): ")
    return [ingredient.strip().lower() for ingredient in ingredients.split(",")]

# function to get trace/uncertain ingredients
def get_maybe_ingredients():
    maybe_ingredients = st.text_input("Does the product label say that it \'may contain\' any ingredients? If so, please list them, separated by commas. If not, please enter \'N/A\': ")
    if maybe_ingredients.lower() == 'n/a' or maybe_ingredients.strip() == "":
        return[]
    return [m.strip().lower() for m in maybe_ingredients.split(",")]

# expand user allergen list using synonyms
def expand_allergen_list(user_allergens):
    expanded = set()
    for allergen in user_allergens:
        if allergen in allergen_synonyms:
            expanded.update(allergen_synonyms[allergen])
        else:
            expanded.add(allergen)  # Add even if not in synonym DB
    return expanded

# function to assign risk
def assign_risk(user_allergens, ingredients, maybe_ingredients):
    risky_ingredients = set(user_allergens) & set(ingredients) # finds common allergens
    maybe_risky_ingredients = set(user_allergens) & set(maybe_ingredients) # find common allergens in 'may contain' list

    if risky_ingredients:
        st.error('Allergens found! Be cautious, the following ingredients you listed as allergies are in this product: ')
        for item in risky_ingredients:
            st.text(f"❌{item.capitalize()}")

    if maybe_risky_ingredients:
        st.warning("\nPotential allergens found! Careful, trace amounts of the following ingredients may exist in this product: ")
        for item in maybe_risky_ingredients:
            st.text(f"⚠️{item.capitalize()}")

        st.text("\nWhat does 'may contain' on the label mean?")
        st.text('\n\'May contain\' is a voluntary statement on food labels that indicates a chance of cross-contamination with an allergen.')
        st.text('This means maybe the same equipment handles all the ingredients, or may have come into contact with the product during manufacturing. It\'s not part of Canadian food allergen labeling regulations.')

    if not risky_ingredients and not maybe_risky_ingredients:
        st.success('✅\nYou\'re all set! No allergen risks found in this food product.')


### MAIN CODE
allergens = get_allergens()
ingredients = get_ingredients()
maybe_ingredients = get_maybe_ingredients()

# button to trigger comparison
if st.button("🔍 Check Allergen Risk"):
    if not allergens or not ingredients:
        st.text("Please fill in both your allergens and the ingredients list before checking.")
    else:
        assign_risk(allergens, ingredients, maybe_ingredients)