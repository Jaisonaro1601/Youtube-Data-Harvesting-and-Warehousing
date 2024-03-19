# Youtube-Data-Harvesting-and-Warehousing
Developing a system to harvest, store, and analyze YouTube data, aiming to glean insights from video metadata, comments, and trends for content performance analysis, trend spotting, and predictive modeling

# Objectives

Data Harvesting: Implement a scalable data harvesting solution that adheres to YouTube's API usage policies. It should be capable of fetching data such as video titles, descriptions, view counts, likes, dislikes, comments, and channel information.

Data Warehousing: Design and deploy a data warehousing solution to store the harvested data efficiently. This includes considering data structuring, indexing, and optimization for fast retrieval and analysis.

Data Analysis and Reporting: Develop tools and scripts for analyzing the warehoused data to extract actionable insights. This may involve trend analysis, sentiment analysis of comments, and performance metrics of different content types.

# Project Overview

This project is designed to harvest data from YouTube, including video statistics, comments, and metadata, for analysis and warehousing purposes. Utilizing YouTube's API, this tool efficiently collects, processes, and stores data in a structured format for further analysis and insight generation.

# Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

# Prerequisites

Python 3.8 or higher.
Streamlit for the web interface.
Access to both MongoDB and PostgreSQL databases.
YouTube Data API key for data harvesting.

# Built with

Python - The core programming language used for data harvesting, processing, and analysis.

Streamlit - Utilized for creating a user-friendly web application to interact with the data.

MongoDB - Employed for storing non-relational data, offering flexibility in data structure and rapid development.

PostgreSQL - Used for structured data warehousing, supporting complex queries and data integrity.

Pandas and NumPy - Python libraries for data manipulation and numerical calculations, facilitating easier data analysis.
  
# Required Libraries

1.googleapiclient.discovery

2.streamlit

3.psycopg2

4.pymongo

5.pandas

# Features

Data Harvesting: Leverages the YouTube Data API to collect detailed information about videos, comments, user statistics, and more, focusing on specific channels or topics.
Data Processing and Normalization: Utilizes Python for data cleaning, processing, and normalization, preparing the data for analysis and storage.
Flexible Data Storage with MongoDB: Stores unstructured or semi-structured data, like comments and video metadata, in MongoDB, allowing for flexible schema and easy scalability.
Structured Data Warehousing with PostgreSQL: Utilizes PostgreSQL for storing structured data, such as video statistics, for complex queries and analysis.
Interactive Web Interface: Features a Streamlit-based web application, making it easy for users to query data, view analytics, and generate reports dynamically.
Automated Data Updates: Includes scheduling capabilities for automated data harvesting and updating, ensuring the dataset remains current.
Analytics and Reporting: Provides basic analytics and customizable reports on the harvested data, leveraging both MongoDB and PostgreSQL for comprehensive insights.
