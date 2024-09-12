# Data Portfolio: Youtube Channel Data Analysis 

# Table of Contents

- [Objectives](#objectives)
- [Data source](#data-source)
- [Stages](#stages)
- [Design](#design)


# Objectives
- What is the key pain point?

The client wants to:
1. Identify what videos are performing the best on their youtube channel
2. Identify what kind of content famous Nigerian food content creators have made this year.

- What is the ideal solution? 
1. Build a dashboard to provide insights in their channel's performance on different metrics such as:
    - view count
    - like count
    - comment count
2. Provide recommendations on content she can upload on their channel.


Metrics
1. views_per_subscribers: Dividing the View count by the subscribers count of the channel
2. likes_per_subscribers: Dividing the Like count by the subscribers count of the channel

# Data source 

- What data is needed to achieve our objective?

We need data on the top Nigerian Food Content Creators in 2024 that includes their:
- channel name
- total subscribers
- video title
- video duration
- date released
- view count
- like count
- comment count


- Where is the data coming from? 
The data is scraped from youtube using the Selenium, BrightData and Youtube API.

# Stages

- Design
- Development
- Testing
- Analysis

# Design

## Dashboard components required
- What should the dashboard contain based on the requirements provided?

To understand what it should contain, we need to figure out what questions we need the dashboard to answer:

1. What videos are getting views higher than the youtuber's subscriber count ?
2. What are the top 10 videos by view count ? 
3. What are the top 10 videos by like count ?
4. What are the top 10 videos by comment count ?
5. How does video length correlate with views/likes/comment?

