import streamlit as st
import streamlit_option_menu
from streamlit_extras.stoggle import stoggle
from processing import preprocess
from processing.display import Main
import requests
import os
import pandas as pd

# The st.set_page_config() function must be the very first Streamlit command.
st.set_page_config(page_title="Aditya Vikram Singh app", layout="wide") 

# This code hides the default Streamlit footer.
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# List of all your files and their corresponding download links
# CONFIRM=1 parameter added to bypass Google Drive's security warning for large files.
FILES_TO_DOWNLOAD = {
    "similarity_tags_genres.pkl": "https://drive.google.com/uc?export=download&id=1nahQKZHpML2NY34qvhvfb2t-A0PVnjwG&confirm=1",
    "movies2_dict.pkl": "https://drive.google.com/uc?export=download&id=1glrH-nYq2rRqKv0XZ9-jnGtMGoWH8as6&confirm=1",
    "new_df_dict.pkl": "https://drive.google.com/uc?export=download&id=17hQHQ8h-WoJK9KMxM2_UC8Ie2oLpHxMw&confirm=1",
    "tmdb_5000_movies.csv": "https://drive.google.com/uc?export=download&id=1GziUgfVsBPF0duXIjBNCG5uRrxaUNJ3R&confirm=1",
    "tmdb_5000_credits.csv": "https://drive.google.com/uc?export=download&id=1UKih_zrpf8IetZtqF-Zp3PrQg8sAjdxl&confirm=1",
    "similarity_tags_keywords.pkl": "https://drive.google.com/uc?export=download&id=1UKih_zrpf8IetZtqF-Zp3PrQg8sAjdxl&confirm=1",
    "similarity_tags_tcast.pkl": "https://drive.google.com/uc?export=download&id=1XcO0Mg_9iELSFfhGh1okvNxc3oal5TnM&confirm=1",
    "similarity_tags_tprduction_comp.pkl": "https://drive.google.com/uc?export=download&id=1x9-De0qQiUZPw5L-i07bqYpngaRKpRo2&confirm=1",
    "similarity_tags_tags.pkl": "https://drive.google.com/uc?export=download&id=15aNXc7_oftnv5_0aqjsdCcijY7fKF8y_&confirm=1",
    "movies_dict.pkl": "https://drive.google.com/uc?export=download&id=1m9GONe0guFk06DRizdPCxagQuge6LR9p&confirm=1"
}

def download_all_files():
    for file_name, file_url in FILES_TO_DOWNLOAD.items():
        if not os.path.exists(file_name):
            st.write(f"Downloading {file_name}...")
            # Use stream=True for large files and allow redirects
            response = requests.get(file_url, stream=True, allow_redirects=True) 
            
            # Check if the download failed (e.g., got a non-file response)
            if response.status_code != 200:
                st.error(f"Failed to download {file_name}. Status: {response.status_code}")
                # We do NOT raise an error here to allow other files to download.
                
            with open(file_name, "wb") as f:
                # Write content in chunks for large files
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            # st.success(f"{file_name} downloaded successfully!") # Removed success message to prevent excessive screen clutter

displayed = []

if 'movie_number' not in st.session_state:
    st.session_state['movie_number'] = 0

if 'selected_movie_name' not in st.session_state:
    st.session_state['selected_movie_name'] = ""

if 'user_menu' not in st.session_state:
    st.session_state['user_menu'] = ""

def main():
    # This must be the first thing that happens inside your main function
    download_all_files()

    def initial_options():
        # To display menu
        st.session_state.user_menu = streamlit_option_menu.option_menu(
            menu_title='What are you looking for? 👀',
            options=['Recommend me a similar movie', 'Describe me a movie', 'Check all Movies'],
            icons=['film', 'film', 'film'],
            menu_icon='list',
            orientation="horizontal",
        )

        if st.session_state.user_menu == 'Recommend me a similar movie':
            recommend_display()

        elif st.session_state.user_menu == 'Describe me a movie':
            display_movie_details()

        elif st.session_state.user_menu == 'Check all Movies':
            paging_movies()

    def recommend_display():

        st.title('Movie Recommender System')

        # new_df is retrieved from the bot.getter() call
        selected_movie_name = st.selectbox(
            'Select a Movie...', new_df['title'].values
        )

        rec_button = st.button('Recommend')
        if rec_button:
            st.session_state.selected_movie_name = selected_movie_name
            recommendation_tags(new_df, selected_movie_name, 'similarity_tags_tags.pkl',"are")
            recommendation_tags(new_df, selected_movie_name, 'similarity_tags_genres.pkl',"on the basis of genres are")
            recommendation_tags(new_df, selected_movie_name,
                                 'similarity_tags_tprduction_comp.pkl',"from the same production company are")
            recommendation_tags(new_df, selected_movie_name, 'similarity_tags_keywords.pkl',"on the basis of keywords are")
            recommendation_tags(new_df, selected_movie_name, 'similarity_tags_tcast.pkl',"on the basis of cast are")

    def recommendation_tags(new_df, selected_movie_name, pickle_file_path,str):

        movies_rec, posters = preprocess.recommend(new_df, selected_movie_name, pickle_file_path)
        st.subheader(f'Best Recommendations {str}...')

        rec_movies = []
        rec_posters = []
        cnt = 0
        # Adding only 5 uniques recommendations
        for i, j in enumerate(movies_rec):
            if cnt == 5:
                break
            if j not in displayed:
                rec_movies.append(j)
                rec_posters.append(posters[i])
                displayed.append(j)
                cnt += 1

        # Columns to display informations of movies i.e. movie title and movie poster
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(rec_movies[0])
            st.image(rec_posters[0])
        with col2:
            st.text(rec_movies[1])
            st.image(rec_posters[1])
        with col3:
            st.text(rec_movies[2])
            st.image(rec_posters[2])
        with col4:
            st.text(rec_movies[3])
            st.image(rec_posters[3])
        with col5:
            st.text(rec_movies[4])
            st.image(rec_posters[4])

    def display_movie_details():
        # Global variables movies and movies2 are needed here, assumed accessible from the Main class.

        selected_movie_name = st.session_state.selected_movie_name
        info = preprocess.get_details(selected_movie_name)

        with st.container():
            image_col, text_col = st.columns((1, 2))
            with image_col:
                st.text('\n')
                st.image(info[0])

            with text_col:
                st.text('\n')
                st.text('\n')
                st.title(selected_movie_name)
                st.text('\n')
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text("Rating")
                    st.write(info[8])
                with col2:
                    st.text("No. of ratings")
                    st.write(info[9])
                with col3:
                    st.text("Runtime")
                    st.write(info[6])

                st.text('\n')
                st.write("Overview")
                st.write(info[3], wrapText=False)
                st.text('\n')
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text("Release Date")
                    st.text(info[4])
                with col2:
                    st.text("Budget")
                    st.text(info[1])
                with col3:
                    st.text("Revenue")
                    st.text(info[5])

                st.text('\n')
                col1, col2, col3 = st.columns(3)
                with col1:
                    str_genres = ""
                    st.text("Genres")
                    for i in info[2]:
                        str_genres = str_genres + i + " . "
                    st.write(str_genres)

                with col2:
                    str_lang = ""
                    st.text("Available in")
                    for i in info[13]:
                        str_lang = str_lang + i + " . "
                    st.write(str_lang)
                with col3:
                    st.text("Directed by")
                    st.text(info[12][0])
                st.text('\n')

        # Displaying information of casts.
        st.header('Cast')
        cnt = 0
        urls = []
        bio = []
        for i in info[14]:
            if cnt == 5:
                break
            url, biography= preprocess.fetch_person_details(i)
            urls.append(url)
            bio.append(biography)
            cnt += 1

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.image(urls[0])
            # Toggle button to show information of cast.
            stoggle(
                "Show More",
                bio[0],
            )
        with col2:
            st.image(urls[1])
            stoggle(
                "Show More",
                bio[1],
            )
        with col3:
            st.image(urls[2])
            stoggle(
                "Show More",
                bio[2],
            )
        with col4:
            st.image(urls[3])
            stoggle(
                "Show More",
                bio[3],
            )
        with col5:
            st.image(urls[4])
            stoggle(
                "Show More",
                bio[4],
            )

    def paging_movies():
        # Global movies variable used here
        # To create pages functionality using session state.
        max_pages = movies.shape[0] / 10
        max_pages = int(max_pages) - 1

        col1, col2, col3 = st.columns([1, 9, 1])

        with col1:
            st.text("Previous page")
            prev_btn = st.button("Prev")
            if prev_btn:
                if st.session_state['movie_number'] >= 10:
                    st.session_state['movie_number'] -= 10

        with col2:
            new_page_number = st.slider("Jump to page number", 0, max_pages, st.session_state['movie_number'] // 10)
            st.session_state['movie_number'] = new_page_number * 10

        with col3:
            st.text("Next page")
            next_btn = st.button("Next")
            if next_btn:
                if st.session_state['movie_number'] + 10 < len(movies):
                    st.session_state['movie_number'] += 10

        display_all_movies(st.session_state['movie_number'])

    def display_all_movies(start):
        # Global movies variable used here
        i = start
        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                id = movies.iloc[i]['movie_id']
                link = preprocess.fetch_posters(id)
                st.image(link, caption=movies['title'][i])
                i = i + 1

            with col2:
                id = movies.iloc[i]['movie_id']
                link = preprocess.fetch_posters(id)
                st.image(link, caption=movies['title'][i])
                i = i + 1

            with col3:
                id = movies.iloc[i]['movie_id']
                link = preprocess.fetch_posters(id)
                st.image(link, caption=movies['title'][i])
                i = i + 1

            with col4:
                id = movies.iloc[i]['movie_id']
                link = preprocess.fetch_posters(id)
                st.image(link, caption=movies['title'][i])
                i = i + 1

            with col5:
                id = movies.iloc[i]['movie_id']
                link = preprocess.fetch_posters(id)
                st.image(link, caption=movies['title'][i])
                i = i + 1

        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                id = movies.iloc[i]['movie_id']
                link = preprocess.fetch_posters(id)
                st.image(link, caption=movies['title'][i])
                i = i + 1

            with col2:
                id = movies.iloc[i]['movie_id']
                link = preprocess.fetch_posters(id)
                st.image(link, caption=movies['title'][i])
                i = i + 1

            with col3:
                id = movies.iloc[i]['movie_id']
                link = preprocess.fetch_posters(id)
                st.image(link, caption=movies['title'][i])
                i = i + 1

            with col4:
                id = movies.iloc[i]['movie_id']
                link = preprocess.fetch_posters(id)
                st.image(link, caption=movies['title'][i])
                i = i + 1

            with col5:
                id = movies.iloc[i]['movie_id']
                link = preprocess.fetch_posters(id)
                st.image(link, caption=movies['title'][i])
                i = i + 1

        st.session_state['page_number'] = i
    
    # Declare new_df, movies, movies2 as global so they can be accessed by the functions above
    global new_df, movies, movies2 

    with Main() as bot:
        bot.main_()
        new_df, movies, movies2 = bot.getter()
        initial_options()

if __name__ == '__main__':
    main()
    import streamlit as st
    st.markdown("<p style='text-align: center; color: grey;'>Built by Aditya vikram singh</p>", unsafe_allow_html=True)
