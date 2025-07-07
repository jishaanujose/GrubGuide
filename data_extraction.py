import json
from serpapi import GoogleSearch
import streamlit as st
serp_api_ren=st.secrets['serp_api_ren']

def hotel_details(query):
    params = {
        "engine": "google_maps",
        "q": query,
        "type": "search",
        "api_key":serp_api_ren
    }

    # search = GoogleSearch(params)
    # results = search.get_dict()
    # with open('sample_serp_search.json', 'w') as f:
    #     json.dump(results, f)
    with open('sample_serp_search.json', 'r') as f:
        results=json.load(f)
    print('---------------')
    print(results)
    print('---------------')
    # Print restaurant names
    hotels=[];all_result=[]
    for result in results.get("local_results", []):
        hotels.append({
            "Title": result.get("title", "N/A"),
            "Location": result.get("address", "N/A"),
            "Status": result.get("open_state", "N/A"),
            "Type": result.get("type", "N/A"),
            'thumbnail':result.get('thumbnail','N/A'),
            'offerings':result.get('offerings','N/A')
        })
        all_result.append(result)
    return hotels,all_result

def review_extraction(data_id):
    search_parameters = {
        "engine": 'google_maps_reviews',
        "data_id": data_id,
        "hl": 'en',
        "api_key": f'{serp_api_ren}',
    }
    # search = GoogleSearch(search_parameters)
    # results = search.get_dict()
    with open('sample_reviws.json', 'r') as f:
        results=json.load(f)
    all_topics = []; all_reviews = [];all_count=[]
    for topics, rev in zip(results['topics'], results['reviews']):
        all_topics.append(topics['keyword'])
        all_count.append(topics['mentions'])
        all_reviews.append(rev['snippet'])
    return all_topics,all_count, '\n'.join(all_reviews)

def image_extraction(hotel):
    search_parameters = {
        "engine": 'google_maps_photos',
        "data_id": hotel['data_id'],
        "hl": 'en',
        "api_key": f'{serp_api_ren}'}
    search = GoogleSearch(search_parameters)
    results = search.get_dict()
    return results
