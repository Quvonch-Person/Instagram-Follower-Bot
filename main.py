import os
from instagram_follower import InstaFollower

# Best practice: Retrieve from environment variables
INSTA_USER = os.environ.get("INSTAGRAM_USERNAME", "your_instagram_username")
INSTA_PASS = os.environ.get("INSTAGRAM_PASSWORD", "your_instagram_password")
TARGET_ACCOUNT = "chefsteps"  # The account whose followers you want to target


def main():
    bot = InstaFollower(
        username=INSTA_USER,
        password=INSTA_PASS,
        target_account=TARGET_ACCOUNT
    )

    bot.login()
    bot.find_followers(scroll_iterations=6)
    bot.follow()


if __name__ == "__main__":
    main()