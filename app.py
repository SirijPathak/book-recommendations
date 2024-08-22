
import pickle

from flask import Flask, render_template, request, jsonify
import numpy as np
import random

popular_df = pickle.load(open('popular_df.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_score = pickle.load(open('similarity_score.pkl', 'rb'))

app = Flask(__name__)

# Store a dictionary to track previously recommended books for each user
recommended_books = {}


@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=popular_df['avg_ratings'].to_list()
                           )


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route("/recommend_books", methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    # Ensure user_input exists in the data
    if user_input not in pt.index:
        return render_template('recommend.html', error="Book not found. Please try again.")

    index = np.where(pt.index == user_input)[0][0]

    # Get previously recommended books for this user (default to empty list)
    previously_recommended = recommended_books.get(user_input, [])

    similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:10]

    # Filter out previously recommended books using set difference
    filtered_similar_items = [item for item in similar_items if pt.index[item[0]] not in previously_recommended]

    # If all similar items have been recommended, shuffle the remaining and choose a subset
    if len(filtered_similar_items) == 0:
        random.shuffle(similar_items)
        filtered_similar_items = similar_items[:5]  # Adjust the number as needed

    # Update recommended books dictionary
    recommended_books[user_input] = [pt.index[i[0]] for i in filtered_similar_items]

    data = []
    for i in filtered_similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(temp_df.drop_duplicates('Book-Title')['Book-Title'].to_list())
        item.extend(temp_df.drop_duplicates('Book-Title')['Book-Author'].to_list())
        item.extend(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].to_list())
        data.append(item)

    return render_template('recommend.html', data=data)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    results = [title for title in popular_df['Book-Title'].unique() if search.lower() in title.lower()]
    return jsonify(results)


if __name__ == '__main__':
    app.run(port=5000)
