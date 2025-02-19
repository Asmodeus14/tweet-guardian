import tweepy
import os
from dotenv import load_dotenv
import time
import requests

# Load API keys from .env file
load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

def create_client():
    try:
        return tweepy.Client(bearer_token=BEARER_TOKEN)
    except Exception as e:
        print(f"Client creation failed: {e}")
        return None

def fetch_tweets(query, count=100, max_retries=3):
    client = create_client()
    if not client:
        return

    for attempt in range(max_retries):
        try:
            response = client.search_recent_tweets(
                query=query,
                max_results=count,
                tweet_fields=["created_at", "text"]
            )
            
            # Process tweets
            if response.data:
                for tweet in response.data:
                    print(f"{tweet.created_at} - {tweet.text}\n{'-'*50}")
            else:
                print("No tweets found.")

            # Print rate limits
            print_rate_limits(response)
            return

        except tweepy.TooManyRequests:
            print(f"Rate limit hit! Waiting 15 minutes...")
            time.sleep(15 * 60)  # Wait 15 minutes
        except (tweepy.TweepyException, requests.exceptions.ConnectionError) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

    print("Max retries exceeded. Giving up.")

def print_rate_limits(response):
    if response.meta:
        print("\nRate Limits:")
        print(f"Remaining: {response.meta.get('result_count', 'N/A')}")  # Number of tweets returned

# Test connection first
def verify_connection():
    try:
        requests.get("https://api.twitter.com", timeout=5)
        print("Network connection to Twitter API successful")
    except Exception as e:
        print(f"Network error: {e}")
        return False
    return True

if __name__ == "__main__":
    if verify_connection():
        print("Starting tweet fetch...")
        fetch_tweets("#ART", count=100)
