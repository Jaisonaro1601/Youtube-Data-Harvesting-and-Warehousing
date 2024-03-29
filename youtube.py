from googleapiclient.discovery import build
import pymongo
import psycopg2
import pandas as pd
import streamlit as st
import plotly.express as px

def Api_connect():
    Api_Id="AIzaSyD4oryTRaxFeCbw3DDzdw870lg0o1Bk_WM"

    api_service_name="youtube"
    api_version="v3"

    youtube=build(api_service_name,api_version,developerKey=Api_Id)

    return youtube
youtube=Api_connect()

#Getting channels information
def get_channel_info(channel_id):
    request=youtube.channels().list(
                    part="snippet,ContentDetails,statistics",
                    id=channel_id
    )
    response=request.execute()

    for i in response['items']:
        data=dict(Channel_Name=i["snippet"]["title"],
                Channel_Id=i["id"],
                Subscribers=i['statistics']['subscriberCount'],
                Views=i["statistics"]["viewCount"],
                Total_Videos=i["statistics"]["videoCount"],
                Channel_Description=i["snippet"]["description"],
                Playlist_Id=i["contentDetails"]["relatedPlaylists"]["uploads"])
    return data

#GETTING VIDEO ID
def get_videos_ids(channel_id):
    video_ids=[]
    response=youtube.channels().list(id=channel_id,
                                    part='contentDetails').execute()
    Playlist_Id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    next_page_token=None

    while True:
        response1=youtube.playlistItems().list(
                                            part='snippet',
                                            playlistId=Playlist_Id,
                                            maxResults=50,
                                            pageToken=next_page_token).execute()
        for i in range(len(response1['items'])):
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token=response1.get('nextPageToken')

        if next_page_token is None:
            break
    return video_ids

#GETTING VIDEO INFORMATION
def get_video_info(video_ids):
    video_data=[]
    for video_id in video_ids:
        request=youtube.videos().list(
            part="snippet,ContentDetails,statistics",
            id=video_id
        )
        response=request.execute()

        for item in response["items"]:
            data=dict(Channel_Name=item['snippet']['channelTitle'],
                    Channel_Id=item['snippet']['channelId'],
                    Video_Id=item['id'],
                    Title=item['snippet']['title'],
                    Tags=item['snippet'].get('tags'),
                    Thumbnail=item['snippet']['thumbnails']['default']['url'],
                    Description=item['snippet'].get('description'),
                    Published_Date=item['snippet']['publishedAt'],
                    Duration=item['contentDetails']['duration'],
                    Views=item['statistics'].get('viewCount'),
                    Likes=item['statistics'].get('likeCount'),
                    Comments=item['statistics'].get('commentCount'),
                    Favorite_Count=item['statistics']['favoriteCount'],
                    Definition=item['contentDetails']['definition'],
                    Caption_Status=item['contentDetails']['caption']
                    )
            video_data.append(data)    
    return video_data


#get comment information
def get_comment_info(video_ids):
    Comment_data=[]
    try:
        for video_id in video_ids:
            request=youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50
            )
            response=request.execute()

            for item in response['items']:
                data=dict(Comment_Id=item['snippet']['topLevelComment']['id'],
                        Video_Id=item['snippet']['topLevelComment']['snippet']['videoId'],
                        Comment_Text=item['snippet']['topLevelComment']['snippet']['textDisplay'],
                        Comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        Comment_Published=item['snippet']['topLevelComment']['snippet']['publishedAt'])
                
                Comment_data.append(data)
                
    except:
        pass
    return Comment_data

def get_playlist_details(channel_id):
        next_page_token=None
        All_data=[]
        while True:
                request=youtube.playlists().list(
                        part='snippet,contentDetails',
                        channelId=channel_id,
                        maxResults=50,
                        pageToken=next_page_token
                )
                response=request.execute()

                for item in response['items']:
                        data=dict(Playlist_Id=item['id'],
                                Title=item['snippet']['title'],
                                Channel_Id=item['snippet']['channelId'],
                                Channel_Name=item['snippet']['channelTitle'],
                                PublishedAt=item['snippet']['publishedAt'],
                                Video_Count=item['contentDetails']['itemCount'])
                        All_data.append(data)

                next_page_token=response.get('nextPageToken')
                if next_page_token is None:
                        break
        return All_data

# upload to mongo db
client=pymongo.MongoClient("mongodb+srv://user:user@cluster0.c1r3fpg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db=client["Youtube_Data"] 

def channel_details(channel_id):
    ch_details=get_channel_info(channel_id)
    pl_details=get_playlist_details(channel_id)
    vi_ids=get_videos_ids(channel_id)
    vi_details=get_video_info(vi_ids )
    com_details=get_comment_info(vi_ids)
    
    coll1=db["channel_details"]
    coll1.insert_one({"channel_information":ch_details,"playlist_information":pl_details,"video_information":vi_details,"comment_information":com_details})
    return "upload completed"

# TABLE CREATION CHANNELS,PLAYLIST,VIDOES,COMMENTS
def channels_table(channel_name_s):
    mydb=psycopg2.connect(host="localhost",
                            user="postgres",
                            password="user",
                            database="youtube_data",
                            port="5432")
    cursor=mydb.cursor()

   
    try:
            create_query='''create table if not exists channels(Channel_Name varchar(100),
                                                                Channel_Id varchar(80) primary key,
                                                                Subscribers bigint,
                                                                Views bigint,
                                                                Total_Videos int,
                                                                Channel_Description text,
                                                                Playlist_Id varchar(80))'''
            cursor.execute(create_query)
            mydb.commit()

    except:
            print("Channels table already created")
    
    single_channel_detail=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({"channel_information.Channel_Name": channel_name_s},{"_id":0}):
        single_channel_detail.append(ch_data["channel_information"])
    df_single_channel_detail=pd.DataFrame(single_channel_detail)

    for index,row in df_single_channel_detail.iterrows():
        insert_query='''insert into channels(Channel_Name ,
                                                    Channel_Id,
                                                    Subscribers,
                                                    Views,
                                                    Total_Videos,
                                                    Channel_Description,
                                                    Playlist_Id)
                                                    
                                                    values(%s,%s,%s,%s,%s,%s,%s)'''
        values=(row['Channel_Name'],
                    row['Channel_Id'],
                    row['Subscribers'],
                    row['Views'],
                    row['Total_Videos'],
                    row['Channel_Description'],
                    row['Playlist_Id']) 
        
        try:
             
            cursor.execute(insert_query,values)
            mydb.commit()
        
        except:
             news=f"Your Provided Channel Name {channel_name_s} is Already Exists"
             return news
        
            
#fetch data FROM PLAYLIST FROM MONGODB AND INSERTED INTO POSTGRE
def playlist_table(channel_name_s):
    mydb=psycopg2.connect(host="localhost",
                            user="postgres",
                            password="user",
                            database="youtube_data",
                            port="5432")
    cursor=mydb.cursor()



    create_query='''create table if not exists playlists(Playlist_Id varchar(100) primary key,
                                                    Title varchar(80),
                                                    Channel_Id varchar(100),
                                                    Channel_Name varchar(100),
                                                    PublishedAt timestamp,
                                                    Video_Count int
                                                        )'''


    cursor.execute(create_query)
    mydb.commit()

    
    single_playlist_details=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({"playlist_information.Channel_Name": channel_name_s },{"_id":0}):
        single_playlist_details.append(ch_data["playlist_information"])
    df_single_playlist_details=pd.DataFrame(single_playlist_details[0])

    
    for index,row in df_single_playlist_details.iterrows():
        insert_query='''insert into playlists(Playlist_Id,
                                            Title ,
                                            Channel_Id,
                                            Channel_Name,
                                            PublishedAt,
                                            Video_Count
                                            )
                                                
                                                values(%s,%s,%s,%s,%s,%s)'''
        values=(row['Playlist_Id'],
                row['Title'],
                row['Channel_Id'],
                row['Channel_Name'],
                row['PublishedAt'],
                row['Video_Count']
            ) 

        cursor.execute(insert_query,values)
        mydb.commit()
    
    


   

    


# fetch data for video information from mongo to postgre
def video_table(channel_name_s):
    mydb=psycopg2.connect(host="localhost",
                            user="postgres",
                            password="user",
                            database="youtube_data",
                            port="5432")
    cursor=mydb.cursor()


    create_query='''create table if not exists videos(Channel_Name varchar(100),
                                                    Channel_Id varchar(100),
                                                    Video_Id varchar(30) primary key,
                                                    Title varchar(150),
                                                    Tags text,
                                                    Thumbnail varchar(200),
                                                    Description text,
                                                    Published_Date timestamp,
                                                    Duration interval,
                                                    Views bigint,
                                                    Likes bigint,
                                                    Comments int,
                                                    Favorite_Count int,
                                                    Definition varchar(10),
                                                    Caption_Status varchar(50)
                                                        )'''



    cursor.execute(create_query)
    mydb.commit()

    single_video_detail=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({"channel_information.Channel_Name":channel_name_s },{"_id":0}):
        single_video_detail.append(ch_data["video_information"])
    df_single_video_detail=pd.DataFrame(single_video_detail[0])

    for index,row in df_single_video_detail.iterrows():
            insert_query='''insert into videos(Channel_Name,
                                                    Channel_Id ,
                                                    Video_Id ,
                                                    Title,
                                                    Tags ,
                                                    Thumbnail ,
                                                    Description ,
                                                    Published_Date ,
                                                    Duration ,
                                                    Views ,
                                                    Likes ,
                                                    Comments ,
                                                    Favorite_Count ,
                                                    Definition,
                                                    Caption_Status 
                                                )
                                                    
                                                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            values=(row['Channel_Name'],
                    row['Channel_Id'],
                    row['Video_Id'],
                    row['Title'],
                    row['Tags'],
                    row['Thumbnail'],
                    row['Description'],
                    row['Published_Date'],
                    row['Duration'],
                    row['Views'],
                    row['Likes'],
                    row['Comments'],
                    row['Favorite_Count'],
                    row['Definition'],
                    row['Caption_Status']
                
            ) 

            cursor.execute(insert_query,values)
            mydb.commit()
    

def comments_table(channel_name_s):
    mydb=psycopg2.connect(host="localhost",
                            user="postgres",
                            password="user",
                            database="youtube_data",
                            port="5432")
    cursor=mydb.cursor()

   
    create_query='''create table if not exists comments(Comment_Id varchar(100) primary key,
                                                        Video_Id varchar(50),
                                                        Comment_Text text,
                                                        Comment_Author varchar(150),
                                                        Comment_Published timestamp
                                                        )'''




    cursor.execute(create_query)
    mydb.commit()

    single_comments_detail=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({"channel_information.Channel_Name":channel_name_s},{"_id":0}):
        single_comments_detail.append(ch_data["comment_information"])
    df_single_comments_detail=pd.DataFrame(single_comments_detail[0])

    for index,row in df_single_comments_detail.iterrows():
                insert_query='''insert into comments(Comment_Id,
                                                        Video_Id ,
                                                        Comment_Text ,
                                                        Comment_Author ,
                                                        Comment_Published 
                                                    )
                                                    
                                                        
                                                    values(%s,%s,%s,%s,%s)'''
                values=(row['Comment_Id'],
                        row['Video_Id'],
                        row['Comment_Text'],
                        row['Comment_Author'],
                        row['Comment_Published']
                    
                ) 

                cursor.execute(insert_query,values)
                mydb.commit()

def tables(singele_channel):
    news=channels_table(singele_channel)
    if news:
         return news
    else:
        playlist_table(singele_channel)
        video_table(singele_channel)
        comments_table(singele_channel)


        return "Tables created successfully"

def show_channels_table():
    ch_list=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    df=st.dataframe(ch_list)
    return df

def show_playlists_table():
    pl_list=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for pl_data in coll1.find({},{"_id":0,"playlist_information":1}):
        for i in range(len(pl_data["playlist_information"])):
            pl_list.append(pl_data["playlist_information"][i])
    df1=st.dataframe(pl_list)
    return df1

def show_videos_table():
    vi_list=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for vi_data in coll1.find({},{"_id":0,"video_information":1}):
        for i in range(len(vi_data["video_information"])):
            vi_list.append(vi_data["video_information"][i])
    df2=st.dataframe(vi_list)
    return df2

def show_comments_table():
    com_list=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
    df3=st.dataframe(com_list)
    return df3

st.markdown("""
<style>
/* Background color for the entire page */
body, .stApp {
    background-color: #ff3b3b!important;
}

/* Sidebar styling */
.css-1d391kg {
    background-color: #f5f5f5;
}

/* Title color in the sidebar */
.css-1aumxhk {
    color: #ff4b4b;
}

/* Custom button styling */
.stButton>button {
    border: 2px solid #4f8bf9;
    border-radius: 20px;
    color: #ffffff;
    background-color: #4f8bf9;
}

/* Text input styling */
.stTextInput>div>div>input {
    border-radius: 20px;
}

/* Customize radio buttons */
.stRadio>div>div {
    background-color: #e0e0e0;
    border-radius: 20px;
    padding: 5px;
}

/* Override default anchor color for better visibility */
a {
    color: #4f8bf9;
}

/* Custom CSS for markdown text to change font-size */
.markdown-text-container {
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)
style = """
<style>
    /* Injecting custom CSS for header */
    .header-style {
        color: #000000;  /* White text color */
        font-size: 24px;
        font-weight: bold; /* Increase font size */
        
    }

    /* Custom styling for markdown text to make it lighter */
    .markdown-style {
        color: #000000; /* Light gray text color for better readability on dark backgrounds */
        font-size: 20px;
        font-weight: bold; /* Adjust font size as needed */
    }
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# Use the custom classes with your header and markdown text
st.markdown('<p class="header-style">YouTube Data Analyzer</p>', unsafe_allow_html=True)
st.markdown('<p class="markdown-style">Welcome to the YouTube Data Analyzer. Please select an option from the sidebar to get started.</p>', unsafe_allow_html=True)

# #streamlit
# with st.sidebar:
#     st.title(":red[YOUTUBE DATA HAVERSTING AND WAREHOUSING]")
#     st.header("Skill Take Away")
#     st.caption("Python Scripting")
#     st.caption("Data Collection")
#     st.caption("MongoDB")
#     st.caption("API Integration")
#     st.caption("Data Management using MongoDB and SQL")

channel_id=st.text_input("Enter the channel ID") 
if st.button("collect and store data"):
    ch_ids=[]
    db=client["Youtube_Data"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_ids.append(ch_data["channel_information"]["Channel_Id"])

    if channel_id in ch_ids:
        st.success("Channel Details of the given channel id already exists")

    else:
        insert=channel_details(channel_id)
        st.success(insert)

all_channels=[]
db=client["Youtube_Data"]
coll1=db["channel_details"]
for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
    all_channels.append(ch_data["channel_information"]['Channel_Name'])
   
unique_channel = st.selectbox("select the channel",all_channels)
if st.button("Migrate to Sql"):
    Table=tables(unique_channel)
    st.success(Table)
show_table=st.radio("SELECT THE TABLE FOR VIEW",("CHANNELS","PLAYLISTS","VIDEOS","COMMENTS"))
if show_table=="CHANNELS":
    show_channels_table()

elif show_table=="PLAYLISTS":
    show_playlists_table()

elif show_table=="VIDEOS":
    show_videos_table()

elif show_table=="COMMENTS":
    show_comments_table()

# SQL COONECTION

mydb=psycopg2.connect(host="localhost",
                    user="postgres",
                    password="user",
                    database="youtube_data",
                    port="5432")
cursor=mydb.cursor()
question=st.selectbox("Select your question",("1. All the videos and the channel name",
                                              "2. channels with most number of videos",
                                              "3. 10 most viewed videos",
                                              "4. comments in each videos",
                                              "5. Videos with higest likes",
                                              "6. likes of all videos",
                                              "7. views of each channel",
                                              "8. videos published in the year of 2022",
                                              "9. average duration of all videos in each channel",
                                              "10. videos with highest number of comments"))

if question =="1. All the videos and the channel name":
    query1='''select title as videos,channel_name as channelname from videos'''
    cursor.execute(query1)
    mydb.commit()
    t1=cursor.fetchall()
    df=pd.DataFrame(t1,columns=["video title","channel name"])
    st.write(df)

elif question =="2. channels with most number of videos":
    query2='''select channel_name as channelname,total_videos as no_videos from channels order by total_videos desc'''
    cursor.execute(query2)
    mydb.commit()
    t2=cursor.fetchall()
    df2=pd.DataFrame(t2,columns=["channel name","No of Videos"])
    st.write(df2)
    fig = px.bar(df2, x='channel name', y='No of Videos', color='No of Videos', title="Channels with Most Number of Videos")

# Set background and paper colors
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',  # Transparent background for the plot
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',  # Transparent background outside the plot
    })

# If you want a solid color instead of transparent, replace 'rgba(0, 0, 0, 0)' with your desired color, e.g., 'rgba(255, 255, 255, 1)' for white.

    st.plotly_chart(fig, use_container_width=True)
    

   
elif question =="3. 10 most viewed videos":
    query3='''select views as views, channel_name as channelname , title as videotitle from videos where views is not null order by  views desc limit 10 '''
    cursor.execute(query3)
    mydb.commit()
    t3=cursor.fetchall()
    df3=pd.DataFrame(t3,columns=["views","channel name","videotitle"])
    st.write(df3)
    fig = px.bar(df3, x='videotitle', y='views', color='channel name',title="10 Most Viewed Videos")
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',  # Transparent background for the plot
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',  # Transparent background outside the plot
    })
    st.plotly_chart(fig, use_container_width=True)

elif question=="4. comments in each videos":
    query4='''select comments as no_comments,title as videotitle from videos where comments is not null'''
    cursor.execute(query4)
    mydb.commit()
    t4=cursor.fetchall()
    df4=pd.DataFrame(t4,columns=["no of comments","videotitle"])
    st.write(df4)

elif question =="5. Videos with higest likes":
    query5='''select title as videotitle, channel_name as channelname,likes as liekcount from videos where likes is not null order by likes desc'''
    cursor.execute(query5)
    mydb.commit()
    t5=cursor.fetchall()
    df5=pd.DataFrame(t5,columns=["videotitle","chennalename","likecount"])
    st.write(df5)
    fig = px.bar(df5.head(10),  # Show top 10 videos for clarity
             y='videotitle',
             x='likecount',
             color='likecount',
             labels={'likecount': 'Likes', 'videotitle': 'Video Title'},
             title="Top 10 Videos with Highest Likes",
             orientation='h',  # Horizontal bar chart
             height=600,  # Adjust height to accommodate the titles
             )

    fig.update_layout(yaxis={'categoryorder': 'total ascending'},  # Sort bars by ascending order of likes
                  plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent plot background
                  paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent paper background
                  )

    fig.update_traces(marker_color='rgb(255, 159, 64)', opacity=0.6)  # Custom bar color and opacity

    st.plotly_chart(fig, use_container_width=True)

elif question =="6. likes of all videos":
    query6='''select likes as likecount, title as videotitle from videos'''
    cursor.execute(query6)
    mydb.commit()
    t6=cursor.fetchall()
    df6=pd.DataFrame(t6,columns=["likecount","videotitle"])
    st.write(df6)
    fig = px.scatter(df6, x='videotitle', y='likecount',
                 title="Likes of All Videos",
                 labels={"videotitle": "Video Title", "likecount": "Likes"})

    # Improve readability:
    fig.update_layout(xaxis_title="Video Title",
                  yaxis_title="Likes",
                  xaxis={'categoryorder':'total descending'},  # This line sorts videos if needed; remove if not desired
                  xaxis_tickangle=-45,  # Rotate labels for better readability
                  plot_bgcolor='rgba(0, 0, 0, 0)',  # Optional: Transparent background for the plot
                  paper_bgcolor='rgba(0, 0, 0, 0)')  # Optional: Transparent background outside the plot

    # Display the plot in the app
    st.plotly_chart(fig, use_container_width=True)

elif question=="7. views of each channel":
    query7='''select channel_name as channelname ,views as totalviews from channels'''
    cursor.execute(query7)
    mydb.commit()
    t7=cursor.fetchall()
    df7=pd.DataFrame(t7,columns=["channel name","totalviews"])
    st.write(df7)
    fig = px.pie(df7, names='channel name', values='totalviews',title="Views Distribution Among Channels")
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',  # Transparent background for the plot
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',  # Transparent background outside the plot
    })
    st.plotly_chart(fig, use_container_width=True)

elif question=="8. videos published in the year of 2022":
    query8='''select title as video_title,published_date as videorelease,channel_name as channelname from videos
                where extract(year from published_date)=2022'''
    cursor.execute(query8)
    mydb.commit()
    t8=cursor.fetchall()
    df8=pd.DataFrame(t8,columns=["videotitle","published_date","channelname"])
    st.write(df8)

elif question=="9. average duration of all videos in each channel":
    query9='''select channel_name as channelname,AVG(duration) as averageduration from videos group by channel_name'''
    cursor.execute(query9)
    mydb.commit()
    t9=cursor.fetchall()
    df9=pd.DataFrame(t9,columns=["channelname","averageduration"])

    T9=[]
    for index,row in df9.iterrows():
        channel_title=row["channelname"]
        average_duration=row["averageduration"]
        average_duration_str=str(average_duration)
        T9.append(dict(channeltitle=channel_title,avgduration=average_duration_str))
    df1=pd.DataFrame(T9)
    st.write(df1)

elif question=="10. videos with highest number of comments":
    query10='''select title as videotitle, channel_name as channelname,comments as comments from videos where comments is
                not null order by comments desc'''
    cursor.execute(query10)
    mydb.commit()
    t10=cursor.fetchall()
    df10=pd.DataFrame(t10,columns=["video title","channel name","comments"])
    st.write(df10)
    fig = px.bar(df10, x='video title', y='comments', color='channel name',title="Videos with Highest Number of Comments")
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',  # Transparent background for the plot
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',  # Transparent background outside the plot
    })
    st.plotly_chart(fig, use_container_width=True)








