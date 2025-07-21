import streamlit as st
import asyncio
import json
from agents import Agent, Runner, function_tool
from connection import config
from whatsapp import send_whatsapp_message

# Standalone function for filtering users
def filter_user_data(min_age: int, user_gender: str, location: str = None, education: str = None) -> list[dict]:
    "Retrieves user data from JSON based on minimum age, user gender, and optional location and education"
    try:
        with open("users.json", "r") as file:
            users = json.load(file)
    except FileNotFoundError:
        st.error("users.json file not found! Please ensure it exists in the same directory.")
        return []
    # Filter by gender and age based on user gender
    if user_gender == "male":
        filtered_users = [user for user in users if user["gender"] == "female" and user["age"] < min_age]
    else:  # user_gender == "female"
        filtered_users = [user for user in users if user["gender"] == "male" and user["age"] > min_age]
    # Apply additional filters
    if location:
        filtered_users = [user for user in filtered_users if user["location"].lower() == location.lower()]
    if education and education.lower() != "other":
        filtered_users = [user for user in filtered_users if user["education"].lower() == education.lower()]
    return filtered_users

# Define a function tool for the agent
@function_tool
def get_user_data(min_age: int) -> list[dict]:
    "Retrieves user data based on minimum age for agent use"
    return filter_user_data(min_age, "male")  # Default to male for agent compatibility

# Define the matchmaking agent
rishte_agent = Agent(
    name="Rishte wali aunty",
    instructions="""
    Tum ek rishtay wali aunty ho. Tumhara kaam yeh hai ke users ki pasand aur zaruraton ke mutabiq unke liye munasib rishtay dhoondhna.
    Choti aur mukhtasir reply do, aur sirf us waqt WhatsApp pe message bhejo jab user khud kahe.
    """,
    tools=[get_user_data, send_whatsapp_message],
)

# Set page configuration
st.set_page_config(page_title="Rishte Wali Aunty", layout="centered")

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'matches' not in st.session_state:
    st.session_state.matches = []

# Header
st.title("Rishte Wali Aunty")
st.write("Apke liye perfect rishta dhoondhne mein madad karein!")

# Input form
st.subheader("Apni Details Batayein")
min_age = st.number_input("Apki Age", min_value=18, max_value=100, step=1, value=20)
user_gender = st.selectbox("Gender", ["Male", "Female"])
location = st.text_input("Location (e.g., Karachi, Lahore)", "")
education = st.selectbox("Education", ["High School", "Bachelor's", "Master's", "PhD", "Other"], index=0)
whatsapp = st.text_input("WhatsApp Number (optional)", "")
submit = st.button("Rishta Dhoondhein", key="submit")

# Process form submission
if submit:
    # Create user input for the agent
    user_input = f"Looking for matches for a {user_gender.lower()} with age {min_age}"
    if location:
        user_input += f", location: {location}"
    if education:
        user_input += f", education: {education}"
    if whatsapp:
        user_input += f", WhatsApp: {whatsapp}"
    
    # Add user input to history
    st.session_state.history.append({"role": "user", "content": user_input})
    
    # Run the agent in an async context
    async def run_agent():
        return await Runner.run(
            starting_agent=rishte_agent,
            input=st.session_state.history,
            run_config=config,
        )
    
    # Execute the async function
    result = asyncio.run(run_agent())
    
    # Add assistant response to history
    st.session_state.history.append({"role": "assistant", "content": result.final_output})
    
    # Update matches using the standalone function
    st.session_state.matches = filter_user_data(min_age, user_gender.lower(), location, education)

# Display matches
if st.session_state.matches:
    st.subheader("Munasib Rishtay")
    for match in st.session_state.matches:
        st.markdown(f"""
        **{match['name'].title()}**  
        Age: {match['age']}  
        Gender: {match['gender'].title()}  
        Location: {match['location']}  
        Education: {match['education']}
        """)
else:
    st.write("Abhi koi rishta nahi mila. Details daal kar dobara try karein!")

# WhatsApp option
if whatsapp:
    if st.button("Send Matches to WhatsApp", key="whatsapp"):
        message = "Found matches:\n" + "\n".join([f"{m['name']} (Age: {m['age']}, Gender: {m['gender'].title()}, Location: {m['location']}, Education: {m['education']})" for m in st.session_state.matches])
        st.session_state.history.append({"role": "user", "content": f"Send to WhatsApp: {message}"})
        async def send_whatsapp():
            return await Runner.run(
                starting_agent=rishte_agent,
                input=st.session_state.history,
                run_config=config,
            )
        result = asyncio.run(send_whatsapp())
        st.session_state.history.append({"role": "assistant", "content": result.final_output})
        st.success("WhatsApp message sent!")