import streamlit as st
import pandas as pd
from fuzzywuzzy import process 

@st.cache_resource()
def card_weight(name, data):
    try:
        all_names = data['name'].tolist()
        best_match, score = process.extractOne(name, all_names)
        #st.write(f'best match for {name} is {best_match}')
        # Attempt to get the weight and handle possible comma separation in the number
        result = int(data[data['name'].str.lower().str.contains(best_match.lower())]['weight'].str.replace(',', '').iloc[0])
    except AttributeError as e:
        # Handle cases where .str.replace might not work (e.g., if the data is already numeric)
        try:
            result = int(data[data['name'].str.lower() == best_match.lower()]['weight'].iloc[0])
        except ValueError as ve:
            # Handle cases where conversion to int fails
            result = 'Invalid Format'
        except IndexError as ie:
            # Handle cases where the index is out of range
            result = 'Not Found'
    except ValueError as ve:
        # Handle cases where conversion to int fails
        result = 'Invalid Format'
    except IndexError as ie:
        # Handle cases where the index is out of range
        result = 'Not Found'
    except Exception as e:
        # General catch-all for any other exceptions
        result = 'Error'
    
    return result

    
def get_weight(card_name, data):
        result = data[data['name'].str.lower() == card_name.lower()]
        if not result.empty:
            return result.iloc[0]['weight']
        else:
            return 'Not Found'

st.title('Brawl Deck Rating')

st.write("Enter your commander:")
commander_input = st.text_input("Enter your commander:")

st.write("Enter your decklist without the commander:")
decklist_input = st.text_area("Deck List", height=99)


card_file_path = 'brawl_card_ratings_27may2024.csv'  
card_data = pd.read_csv(card_file_path)


commander_file_path = 'brawl_commander_ratings_27may2024.csv'
commander_data = pd.read_csv(commander_file_path)

if st.button('Get Weights'):
    
    deck_score = {}
    # Get weight for the commander
    commander_weight = card_weight(commander_input, commander_data)
    st.write(f"Commander: {commander_input} - Weight: {commander_weight}")
    deck_score[commander_input] = commander_weight

    # Get weights for the decklist
    decklist_items = decklist_input.split('\n')
    decklist_weights = {}
    for item in decklist_items:
        item = item.strip()
        if item:  # Avoid empty lines
            item = item.split(' ', 1)
            name = str(item[1])
            count = int(item[0])
            card_score = card_weight(name, card_data)
        
            deck_score[name] = card_score * count

    
    # Display the weights for the decklist
    st.write("Decklist Weights:")
    st.write(deck_score)
    total_score = sum(deck_score.values())
    st.markdown(f"Total Score: __{total_score}__")

exp = st.expander('Click to see lookup tables:')
with exp:
    st.dataframe(card_data, use_container_width=True)
    st.dataframe(commander_data, use_container_width=True)
