import streamlit as st
import requests
import time
from datetime import datetime
import pandas as pd
import json

# API Configuration
API_URL = "http://localhost:8000"  # FastAPI backend URL

def get_user_stats(user_id: int):
    try:
        response = requests.get(f"{API_URL}/users/{user_id}/stats")
        return response.json()
    except Exception as e:
        st.error(f"Error fetching user stats: {str(e)}")
        return {
            "total_minutes": 0,
            "previous_total": 0,
            "today_total": 0,
            "current_streak": 0,
            "monthly_progress": []
        }

def get_user_routines(user_id: int):
    try:
        response = requests.get(f"{API_URL}/users/{user_id}/routines")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching routines: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to server: {str(e)}")
        return []

def save_routine(user_id: int, routine_data: dict):
    try:
        response = requests.post(f"{API_URL}/users/{user_id}/routines", json=routine_data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error saving routine: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to server: {str(e)}")
        return None

def generate_activity(user_profile: dict):
    try:
        # Convert interests list to comma-separated string
        user_profile = user_profile.copy()
        if 'interests' in user_profile and isinstance(user_profile['interests'], list):
            user_profile['interests'] = ','.join(user_profile['interests'])
        
        response = requests.post(f"{API_URL}/generate-activity", params=user_profile)
        if response.status_code == 422:
            st.error("Invalid input parameters. Please check your selections.")
            return None
        return response.json()
    except Exception as e:
        st.error(f"Error generating activity: {str(e)}")
        return {
            "text": "Unable to generate activity at the moment. Please try again.",
            "duration": user_profile.get('time_available', 10),
            "category": "Error"
        }

def generate_stress_relief(stress_trigger: str, stress_level: int):
    try:
        response = requests.post(
            f"{API_URL}/generate-stress-relief", 
            params={"stress_trigger": stress_trigger, "stress_level": stress_level}
        )
        return response.json()
    except Exception as e:
        st.error(f"Error generating stress relief: {str(e)}")
        return {"practice": "Unable to generate stress relief practice at the moment."}

def generate_sleep_practice(sleep_quality: str, stress_level: int):
    try:
        response = requests.post(
            f"{API_URL}/generate-sleep-practice",
            params={"sleep_quality": sleep_quality, "stress_level": stress_level}
        )
        return response.json()
    except Exception as e:
        st.error(f"Error generating sleep practice: {str(e)}")
        return {"practice": "Unable to generate sleep practice at the moment."}

def complete_activity(user_id: int, activity_id: int, mood_after: str = None):
    try:
        response = requests.post(
            f"{API_URL}/users/{user_id}/activities/{activity_id}/complete",
            params={"mood_after": mood_after} if mood_after else None
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error completing activity: {str(e)}")
        return False

def save_activity(user_id: int, activity_data: dict):
    try:
        response = requests.post(
            f"{API_URL}/users/{user_id}/activities",
            json=activity_data
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error saving activity: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error saving activity: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Mindful Moments",
        page_icon="🧘",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Session State
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 1
    if 'current_activity' not in st.session_state:
        st.session_state.current_activity = None
    
    st.title("🧘 Mindful Moments")
    
    tabs = st.tabs(["Practice", "Progress", "Settings"])
    
    with tabs[0]:  # Practice Tab
        # Create two columns for better organization
        left_col, right_col = st.columns([2, 1])
        
        with left_col:
            st.markdown("### 🎯 Quick Practice")
            
            # Group related inputs in expanders
            with st.expander("Your Current State", expanded=True):
                mood = st.select_slider(
                    "How are you feeling right now?",
                    options=["Very Low", "Low", "Neutral", "Good", "Excellent"],
                    value="Neutral",
                    key="current_mood"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    energy = st.slider("Energy Level", 1, 10, 5, key="energy_level")
                with col2:
                    stress = st.slider("Stress Level", 1, 10, 5, key="stress_level")
                
                time_available = st.select_slider(
                    "How much time do you have?",
                    options=[5, 10, 15, 20, 30, 45, 60],
                    value=10,
                    key="time_available"
                )
            
            with st.expander("Your Interests", expanded=True):
                custom_interest = st.text_input("Add a new interest:", key="custom_interest_input")
                default_interests = ["Meditation", "Yoga", "Nature", "Reading", "Art", "Music", "Breathing", "Walking", "Journaling", "Body Scan"]
                
                if custom_interest:
                    if custom_interest not in default_interests:
                        default_interests.append(custom_interest)
                        st.success(f"Added '{custom_interest}' to your interests!")
                
                interests = st.multiselect(
                    "Select or add interests:",
                    options=default_interests,
                    default=["Meditation"],
                    key="interests_multiselect"
                )
        
        with right_col:
            st.markdown("### 🔄 Your Routines")
            
            # Get user's routines from API
            user_routines = get_user_routines(st.session_state.user_id)
            
            # Display routines
            for routine in user_routines:
                with st.container():
                    st.markdown(f"**{routine['name']}** ({routine['duration']} min)")
                    st.caption(f"{routine['description']}")
                    if st.button("Start", key=f"routine_{routine['id']}", use_container_width=True):
                        st.session_state.current_activity = {
                            'category': routine['category'],
                            'text': "STEPS:\n" + "\n".join([f"{i+1}. {step}" for i, step in enumerate(routine['steps'])]),
                            'duration': routine['duration']
                        }
                        st.rerun()
            
            st.divider()
            with st.expander("✨ Create New Routine", expanded=False):
                new_routine_name = st.text_input("Routine Name", key="new_routine_name")
                new_routine_duration = st.number_input("Duration (minutes)", min_value=1, value=10, key="new_routine_duration")
                new_routine_steps = st.text_area("Steps (one per line)", key="new_routine_steps")
                
                if st.button("Save New Routine", key="save_new_routine_button"):
                    if new_routine_name and new_routine_steps:
                        steps = [step.strip() for step in new_routine_steps.split('\n') if step.strip()]
                        if steps:
                            new_routine = {
                                'name': new_routine_name,
                                'steps': steps,
                                'duration': new_routine_duration,
                                'category': 'Custom',
                                'description': f"Custom {new_routine_duration}-minute routine"
                            }
                            if save_routine(st.session_state.user_id, new_routine):
                                st.success("Routine saved successfully!")
                                st.rerun()
                        else:
                            st.warning("Please add at least one step to your routine")
                    else:
                        st.warning("Please provide both a name and steps for your routine")

        st.divider()
        
        # Generate Activity button
        if st.button("Generate Personalized Activity", key="generate_activity_button", use_container_width=True):
            user_profile = {
                'mood': mood,
                'energy_level': energy,
                'stress_level': stress,
                'time_available': time_available,
                'interests': interests
            }
            
            with st.spinner("Creating your personalized mindful moment..."):
                activity = generate_activity(user_profile)
                if activity:
                    # Save the activity to get an ID
                    saved_activity = save_activity(st.session_state.user_id, activity)
                    if saved_activity:
                        st.session_state.current_activity = {
                            **saved_activity,
                            'text': activity['text'],
                            'category': activity['category']
                        }
                        st.rerun()

        # Quick Access Features
        quick_access = st.expander("🚀 Quick Access Features", expanded=True)
        with quick_access:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("⚡ Stress Relief")
                stress_trigger = st.text_input("What's causing stress right now?")
                if st.button("Get Quick Relief Practice"):
                    with st.spinner("Generating stress relief practice..."):
                        response = generate_stress_relief(stress_trigger, stress)
                        if response and 'practice' in response:
                            st.markdown(response['practice'])
            
            with col2:
                st.write("😴 Better Sleep")
                sleep_quality = st.select_slider(
                    "Recent sleep quality?",
                    options=["Poor", "Fair", "Good", "Excellent"],
                    value="Fair"
                )
                if st.button("Get Bedtime Practice"):
                    with st.spinner("Generating sleep practice..."):
                        response = generate_sleep_practice(sleep_quality, stress)
                        if response and 'practice' in response:
                            st.markdown(response['practice'])
        
        # Display current activity if exists
        if st.session_state.current_activity:
            st.markdown("### 🎯 Current Activity")
            if isinstance(st.session_state.current_activity, dict):
                if 'category' in st.session_state.current_activity:
                    st.markdown(f"**Category:** {st.session_state.current_activity['category']}")
                if 'text' in st.session_state.current_activity:
                    st.markdown(st.session_state.current_activity['text'])
                if 'duration' in st.session_state.current_activity:
                    st.markdown(f"**Duration:** {st.session_state.current_activity['duration']} minutes")
            else:
                st.markdown(str(st.session_state.current_activity))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Complete Activity", use_container_width=True):
                    if 'id' in st.session_state.current_activity:
                        if complete_activity(
                            st.session_state.user_id,
                            st.session_state.current_activity['id']
                        ):
                            st.success("Activity completed! Great job! 🎉")
                            st.session_state.current_activity = None
                            st.rerun()
                    else:
                        st.session_state.current_activity = None
                        st.rerun()
            with col2:
                if st.button("Cancel Activity", use_container_width=True):
                    st.session_state.current_activity = None
                    st.rerun()

    with tabs[1]:  # Progress Tab
        st.markdown("### 📊 Your Progress")
        
        # Get user stats from API
        stats = get_user_stats(st.session_state.user_id)
        
        # Display stats in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Practice Time", f"{stats['total_minutes']} min")
        with col2:
            st.metric("Today's Practice", f"{stats['today_total']} min")
        with col3:
            st.metric("Current Streak", f"{stats['current_streak']} days")
        with col4:
            monthly_total = sum(day['minutes'] for day in stats['monthly_progress'])
            st.metric("This Month", f"{monthly_total} min")

    with tabs[2]:  # Settings Tab
        st.markdown("### ⚙️ Settings")
        # Add settings UI here

if __name__ == "__main__":
    main() 