import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class BookRecommender:
    def __init__(self, data_path):
        self.books_data = pd.read_csv(data_path)
        self.books_data = self.books_data[:1000]
        self.df = self.books_data.copy()
        self.df.reset_index()

    def _combine_features(self, row):
        try:
            return row['title'] + " " + row['author'] + " " + row['genres']
        except Exception as e:
            print("Error:", e)

    def recommend(self, bookmarked_book):
        # Features can be genre and title
        features = ['title', 'author', 'genres']
        for feature in features:
            self.df[feature] = self.df[feature].fillna('')
        self.df["combined_features"] = self.df.apply(self._combine_features, axis=1)
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(self.df["combined_features"])
        cosine_sim = cosine_similarity(count_matrix)
        indexnum = self.df[self.df['title'] == bookmarked_book].index[0]
        similar_books = list(enumerate(cosine_sim[indexnum]))
        sorted_similar_books = sorted(similar_books, key=lambda x: x[1], reverse=True)
        recomlist = [self.df['title'][sorted_similar_books[i][0]] for i in range(1, 10)]
        return recomlist

if __name__ == "__main__":
    # The name should come once the bookmark is done
    recommender = BookRecommender("C:\\Users\\Dell\\Desktop\\books_1.Best_Books_Ever.csv")
    newlist = recommender.recommend("The Golden Compass")
    print(newlist)
