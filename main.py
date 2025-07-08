import streamlit as st
import matplotlib.pyplot as plt
from knowledge_creation import load_profiles, save_profiles, update_user_profile, get_user_profile
from user_location import get_current_location
from LLM_agent import extract_profile_from_chat, get_intent_from_llm
from data_extraction import hotel_details, review_extraction, image_extraction
from data_preprocess import get_all_info
import base64
from audio_recorder_streamlit import audio_recorder
from STT_agent import speech_to_text

def sidebar_bg(side_bg):

   main_bg_ext = 'jpg'

   st.markdown(
       f"""
            <style>
            .stApp {{
                background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
                background-size: cover
            }},
            </style>
            """,
       unsafe_allow_html=True
   )

def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    #text = link.split('=')[1]
    print(link)
    return f'<a target="_blank" href="{link}"</a>'

def show_images_horizontally(url_list):
    cols = st.columns(len(url_list))
    for col, url in zip(cols, url_list):
        col.image(url, use_container_width=True)


st.set_page_config(page_title="Hotel Finder", layout="wide")
side_bg = 'bckg.jpg'
sidebar_bg(side_bg)

if "selected_hotel" not in st.session_state:
    st.session_state.selected_hotel = None
if "query" not in st.session_state:
    st.session_state.query = None
if "user_det" not in st.session_state:
    st.session_state.user_details = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "serp_results" not in st.session_state:
    st.session_state.serp_results = None

st.title("GRUBGUIDE")
st.write('Your Smart Restaurant & Hotel Assistant')
st.sidebar.image('logo.png',width=400)
user=st.text_input('Enter username:')
if user:
    user_identity=get_user_profile(user)
    if user_identity=={}:
            food_type=st.text_input('Enter preferred food type:')
            if food_type:
                update_user_profile(user, "preferred_locations", '')
                update_user_profile(user, 'food_preferences', food_type)
                user_identity = get_user_profile(user)
                st.session_state.user_details = user_identity
                st.success("User saved!")
    else:
        user_identity['user']=user
        st.session_state.user_details=user_identity
        st.write('Loaded user details')

if st.session_state.selected_hotel is None:
    user_identity=st.session_state.user_details

    if user_identity!={} and user_identity['food_preferences'] !='':
        st.subheader("🤖 Recommendations based on preference and user location:")
        with st.container(border=True):
            loc = get_current_location()
            query_recommend = f'Search for hotels in or near **{loc['city']}, {loc['region']}, {loc['country']}** which provides **{user_identity['food_preferences']}** food'
            st.write(query_recommend)
            recomm=st.button("Search", type="primary")
        col1, col2,col3,_,_,_,_ = st.columns(7)
        button1 = col1.button('New chat',type="primary")
        button2 = col2.button('Refresh',type="primary")
        #button3 = col3.button('Refresh', type="primary")
        if recomm:
            query=query_recommend
            st.session_state.query = query
        if button1:
            st.session_state.query=''
        if button2:
            st.session_state.selected_hotel = None
            st.session_state.query = None
            st.session_state.user_details = {}
            st.session_state.chat_history = []
            st.rerun()
    if st.session_state.query=='':
        col1, col2 = st.columns([8, 0.45])
        with col1:
            query = st.text_input("What do you want to search:")
        with col2:
            st.markdown("###### ")  # spacing
            audio_bytes = audio_recorder(text="", recording_color="#e8b62c",neutral_color="#6aa36f",icon_size="sm")
            #audio_bytes = audio_recorder(text="Click for voice search", recording_color="#e8b62c",neutral_color="#6aa36f",icon_name="microphone")
            if audio_bytes:
                with open('audio.wav', "wb") as f:
                    f.write(audio_bytes)
                # st.success(f"🎙 Audio Recorded!")
                query=speech_to_text('audio.wav')
        if audio_bytes:
           st.write(f'User query : {query}')
        st.session_state.query=query
    if st.session_state.query:
            query=st.session_state.query
            user_profile=extract_profile_from_chat(query)
            update_user_profile(user_identity['user'], "preferred_locations", user_profile['location'])
            if user_profile['cuisine'] is not None:
                update_user_profile(user_identity['user'], "food_preferences", user_profile['cuisine'])
            prompt='''You are a helpful assistant who help to understand what does the user want to do. \n
                        Extract and return in a single liner just the key intention of the user like what, where, what time. Return ONLY the single liner intention.'''
            intent = get_intent_from_llm(query,prompt)
            if "restaurant" in intent or "hotel" in intent or "ice cream" in intent or "food court" in intent or "food" in intent:
                #hotels,all_results = hotel_details(intent)
                if st.session_state.serp_results is None:
                    hotels, all_results = hotel_details(intent)
                    st.session_state.serp_results = (hotels, all_results)
                else:
                    hotels, all_results = st.session_state.serp_results
                st.subheader("Search results:")
                for id,hotel in enumerate(hotels):
                    cols = st.columns([1, 4])
                    with cols[0]:
                        if "thumbnail" in hotel:
                            st.image(hotel["thumbnail"], width=100)
                        else:
                            st.write("No Image")
                    with cols[1]:
                        st.subheader(hotel["Title"])
                        st.write(hotel.get("Location", ""))
                        st.write("Status:", hotel.get("open_state", "Unknown"))
                        st.write("Type:", hotel.get("type", ""))
                        if st.button(f"View Details: {hotel['Title']}"):
                            st.session_state.selected_hotel = all_results[id]
                            # print(st.session_state.selected_hotel)
                            st.rerun()
            else:
                st.error('Cannot load details asked. Can help for finding food courts or hotels!')
else:
        hotel = st.session_state.selected_hotel
        st.header(hotel["title"])
        st.image(hotel.get("thumbnail", ""))
        st.write("📍 Address:", hotel.get("address", ""))
        st.write("📍 Contact:", hotel.get("phone", ""))
        st.write("✅ Status:", hotel.get("Status", "Unknown"))
        st.write("🍽️ Type:", hotel.get("Type", "Unknown"))
        if hotel.get('order_online') is not None:
            st.markdown(
                "<h1 style='font-size: 30px;'>🍕🚚 </h1>",
                unsafe_allow_html=True
            )
            st.markdown(f"[**Order Online**]({hotel.get('order_online')})", unsafe_allow_html=True)
        with st.container(border=True):
            # print(hotel.get('offerings'))
            if hotel.get('offerings') is not None:
                st.write("🍽️ Offerings:",hotel.get('offerings'))
            else:
                st.write("🍽️ Offerings:", f'Menu not available online. Please call {hotel.get("phone", "")}')

        all_text_content=get_all_info(hotel)
        # Optional: Detailed review (if available)
        st.subheader("📊 Number of User reviews and rating")
        if "reviews" in hotel:
            st.write(f"🗣️ **Count of user reviews**: {hotel['reviews']}")
        fig, ax1 = plt.subplots(figsize=(1, 1))
        if "rating" in hotel:
            rating = hotel['rating']
            data = [rating, 5 - rating]
            colors = ['green', 'lightgrey']
            wedges, _ = ax1.pie(data, startangle=90, colors=colors, wedgeprops=dict(width=0.1))
            ax1.text(0, 0, f"{rating}", ha='center', va='center', fontsize=12)
            ax1.set(aspect="equal")
            plt.title("⭐ Rating")
            file_path = "cuisine_pie_chart.png"
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            st.image("cuisine_pie_chart.png")
        all_topics,all_count,reviews=review_extraction(hotel['data_id'])
        all_text_content+=reviews
        more_image=st.button('Need more images?')
        if more_image:
            results=image_extraction(hotel)
            all_url = []
            for url in results['photos']:
                all_url.append(url['thumbnail'])

            show_images_horizontally(all_url[:5])
        st.subheader("❓ Queries:")
        with st.container(border=True):
            user_input = st.text_input("Ask something about the hotel:")
            if user_input:
                # Use LLM call here
                prompt = f"Based on the following content:\n{all_text_content}.\nGive answer to the given query. If no information found, return as 'No information found'."

                # Fake LLM call placeholder
                answer = get_intent_from_llm(user_input,prompt)

                # Store in memory
                st.session_state.chat_history.append(("User", user_input))
                st.session_state.chat_history.append(("Assistant", answer))

        # Display chat
        for role, msg in st.session_state.chat_history:
            st.markdown(f"**{role}:** {msg}")

        # Add back button
        if st.button("🔙 Back to list"):
            st.session_state.selected_hotel = None
            st.session_state.chat_history=[]
            st.rerun()
