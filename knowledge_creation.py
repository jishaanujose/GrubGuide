import json
import os

PROFILE_FILE = "user_profiles.json"

# Load profiles from disk
def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'w') as f:
            json.dump({}, f)
    with open(PROFILE_FILE, 'r') as f:
        return json.load(f)

    return {}

# Save profiles to disk
def save_profiles(profiles):
    with open(PROFILE_FILE, 'w') as f:
        json.dump(profiles, f, indent=4)

# Update a user's profile
def update_user_profile(user_id, key, value):
    profiles = load_profiles()
    if user_id not in profiles:
        profiles[user_id] = {}
    profiles[user_id][key] = value
    save_profiles(profiles)

# Get a user's profile
def get_user_profile(user_id):
    profiles = load_profiles()
    return profiles.get(user_id, {})