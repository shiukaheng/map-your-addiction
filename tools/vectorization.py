from parse_history import parse_history_file_altered as parse_history_file
from comment_fetcher import get_video_comments_batch2
import pickle
import unicodedata
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
import matplotlib as mpl
import matplotlib.pyplot as plt

# ----- Constants and plot settings
plt.style.use('dark_background')
mpl.use('TkAgg') # Leave this uncommented for interactive plots on Pycharm
# Stopwords are words that are ignored because they are usually not correlated with a certain topic
stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
# ---------------------------------


def generate_history_with_comments(input_html_path, output_pickle_path, max_videos=None, max_pages=3):
    history = parse_history_file(input_html_path)[:max_videos]
    history = get_video_comments_batch2(history, max_pages=max_pages)
    with open('history.pickle', 'wb') as file:
        pickle.dump(history, file)


def load_pickle(pickle_path):
    with open(pickle_path, 'rb') as file:
        data = pickle.load(file)
    return data


def visualize(history_with_comments, max_features=2000,  n_iter=5000, perplexity=150):
    # Cull videos that have less than 60 comments
    history = [x for x in history_with_comments if len(x['comments']) >= 60]
    # Sort videos by watch time
    history = sorted(history, key=lambda x: x["access_time"])
    # Merge all comments as single string for every video and remove breaks
    for video in history:
        video['merged_comments'] =  " ".join(video['comments']).replace("\n", " ")
    # Convert to TFIDF normalized bag of words
    vectorizer = TfidfVectorizer(stop_words=stopwords, max_features=max_features)
    X = vectorizer.fit_transform([x['merged_comments'] for x in history])
    # T-SNE dimension reduction to 2 dimensions
    tsne = TSNE(n_components=2, verbose=1, n_iter=n_iter, perplexity=perplexity)
    processed2 = tsne.fit_transform(X)
    # print(processed2.shape)
    fig, ax = plt.subplots()

    ax.scatter(*np.transpose(processed2))
    # plt.plot(*np.transpose(processed2))
    for i, txt in enumerate(processed2):
        ax.annotate(history[i]['video_title'], (txt[0], txt[1]))
    plt.title("Youtube history map")
    plt.tight_layout()
    fig = plt.gcf()
    fig.set_size_inches(30,30)
    plt.savefig("fig.png", dpi=500, pad_inches = 0)
    # plt.show()
    # Check plot and see if you find clusters!

if __name__ == "__main__":
    # generate_history_with_comments("watch-history.html", "history.pickle", max_videos=600)
    history_w_comments = load_pickle("history.pickle")
    visualize(history_w_comments, max_features=2000, n_iter=10000, perplexity=400)
