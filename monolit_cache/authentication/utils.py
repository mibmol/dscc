
"""
def facebook_check_token_url(input_token, access_token):
    return f"https://graph.facebook.com/debug_token?input_token={input_token}&access_token={access_token}"

def facebook_access_token_url():
    return f'https://graph.facebook.com/oauth/access_token?client_id=938330693354202&grant_type=client_credentials&client_secret=e18d9caed6bc7816294bc22af9a29dc3'
"""
from datetime import datetime, timedelta

def get_now_delta(minutes=0, hours=0, days=0, seconds=0):
    return datetime.now() + timedelta(minutes=minutes, days=days, seconds=seconds, hours=hours)