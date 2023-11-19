import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend(bookmarked_book):
	
	#Database part
	books = pd.read_csv(r"C:\\Users\\Dell\\Documents\\Books.csv")
	books=books[:10000]
	df=books

	df.reset_index()

	#Finding index of the bookmark
	indexnum=df[df['Title'] == bookmarked_book].index[0]

	#Features can be genre and title
	features = ['Title','Author','Publisher']
	for feature in features:
		df[feature] = df[feature].fillna('')
	
	def combine_features(row):
		try:
			return row['Title'] +" "+row['Author']+" "+row['Publisher']
		except:
			print("Error:", row)

	df["combined_features"] = df.apply(combine_features,axis=1)
	
	cv = CountVectorizer()
	count_matrix = cv.fit_transform(df["combined_features"])

	cosine_sim = cosine_similarity(count_matrix) 
	
	similar_books = list(enumerate(cosine_sim[indexnum]))
	
	sorted_similar_books = sorted(similar_books,key=lambda x:x[1],reverse=True)

	recomlist=[]

	for i in range(1,10):
		title=sorted_similar_books[i]
		titlenumber=title[0]
		recomlist.append(df['Title'][titlenumber])

	return recomlist

if __name__=="__main__":
	#The name should come once the bookmark is done
	newlist=recommend("Harry Potter and the Sorcerer's Stone (Harry Potter (Paperback))")
	print(newlist)