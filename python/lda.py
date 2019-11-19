"""This file contains code for a latent dirichlet allocation (SLDA),
which uses principles from maximum likelihood estimation and
Expectation-Maximization."""

# Native Python imports
import os
import copy

# External package imports
import numpy as np
import cv2 as cv
import pickle

# External package imports
import numpy as np
import cv2 as cv
from sklearn.decomposition import LatentDirichletAllocation as LDA
from sklearn.cluster import KMeans
from scipy.special import kl_div

# Custom module imports
#import dataset
import feature_extraction
import crop_images

#n_keypoints = 100
n_keypoints=49*4
class LDA2:
    """Class that implements Latent Dirichlet Allocation using an
    Expectation-Maximization framework.  This function iterates through the
    following two steps to find a locally-optimal maximum likelihood estimate of
    the relevant posterior distribution.

    Arguments:
        features: A numpy array of size (N_images x N_descriptors)
        alpha (float): A parameter for our LDA model (TODO: add on here).
        beta (float): A parameter for our LDA model (TODO: add on here).

    """
    # TODO: How do we represent the cardinality of our "vocabulary"
    def __init__(self, data_path, feature_path, alpha=1, beta=1, eps=1e-5,
                 n_topics=10, V=100):
        self.data_path = data_path  # File path for data
        self.feature_path = feature_path
        self.alpha = alpha  # Dirichlet dist hyperparameter
        self.beta = beta  # Dirichlet dist hyperparameter
        self.log_likelihood = None  # Array of log likelihoods
        self.parameters = None  # Numpy vector of parameters
        self.eps = eps  # Convergence threshold
        self.keypoints = None
        self.k_topics = n_topics
        self.get_data_matrix()  # Call in constructor method
        self.m_documents = self.M.shape[0]
        self.vocab_size = V
        self.init_LDA()  # Call in constructor method

    def get_data_matrix(self):
        with open(self.feature_path, 'rb') as f:
            self.M = pickle.load(f)
        self.m_documents =

    def off_the_shelf_LDA(self):
        lda = LDA(n_components=self.n_topics)
        lda.fit(self.M)
        return lda

    def init_LDA(self):
        self.M_word_topic = np.zeros((self.k_topics, self.m_documents)) #(k x m)
        self.M_topic_vocab = np.zeros((self.k_topics, self.vocab_size)) #(k x v)
        self.M_count_k = np.zeros((self.k_topics, 1))  # (k x 1)

        # Now we need to randomly initialize documents and vocab over topics
        self.document_topics = np.random.randint(1, self.k_topics,
                                                 size=(self.k_topics,
                                                       self.m_documents))
        # TODO: FINISH THIS

    def compute_conditional_dist(self, m, n):
        # Return a probability distribution for word n in document m
        # belonging to a topic
        vector = [self.M_word_topic[k,m]


    def sample_phi_from_dirichlet(self, n=1):
        """Function to sample from a Dirichlet distribution.

        Arguments:
            n (int): The number of samples from the Dirichlet distribution
                this function returns.

        Returns:
            A np array of samples from the Dirichlet distribution, of size n.
        """

        return np.random.dirichlet(self.beta, size=n)

    def gibbs_sampler(self, T):
        for t in T:  # Iterate over timesteps
            for i in
                pass


    def sample_pi_from_dirichlet(self, n=1):
        """Function to sample from a Dirichlet distribution.

        Arguments:
            n (int): The number of samples from the Dirichlet distribution
                this function returns.

        Returns:
            A np array of samples from the Dirichlet distribution, of size n.
        """

        return np.random.dirichlet(self.alpha, size=n)

    def find_params(self):
        """Function that iterates over the expectation and maximization steps
        until the parameter estimates converge to their optimal set."""

        old_params = np.zeros(self.parameters.shape)

        # Iterate until our parameters converge
        while np.linalg.norm(old_params - new_params) > self.eps:
            # Take expectation step
            self.expectation_step()

            # Take maximization step
            self.maximization_step()

            old_params = copy.deepcopy(self.parameters)

        return self.parameters

def evaluate_performance(cluster_predictions, actual_dic, actual_labels):
    """Given the cluster_predictions, that maps id:cluster, actual_dic that maps id:label
    and actual_labels which is all the labels in actual_dic, returns a count of label:count
    that is found in the cluster."""
    count = {i: 0 for i in actual_labels}
    for k in cluster_predictions:
        label = actual_dic[k]
        count[label] += 1
    return count

def compute_symmetric_KL(dist_a, dist_b):
    return 0.5 * (kl_div(dist_a, dist_b)) + 0.5 * (kl_div(dist_b, dist_a))

def evaluate_main():
    labels = ["06c54", "011k07", "099ssp"] #labels in descriptors_test_1
    m_dir = "/home/yaatehr/programs/spatial_LDA/data/cropped_test_0/m/"
    data_dir = '/home/yaatehr/programs/spatial_LDA/data/'
    actual_dic = {}
    for l in labels:
        label_path = os.path.join(m_dir, l)
        print(label_path)
        dic = crop_images.map_image_id_to_label(label_path, l)
        actual_dic.update(dic)
    with open(os.path.join(data_dir, "cluster_0_predictions1.pkl"), "rb") as f:
        cluster_0_dic = pickle.load(f)
    cluster_0_count = evaluate_performance(cluster_0_dic, actual_dic, labels)
    print("cluster 0 count: ", cluster_0_count)
    with open(os.path.join(data_dir, "cluster_1_predictions1.pkl"), "rb") as f:
        cluster_1_dic = pickle.load(f)
    cluster_1_count = evaluate_performance(cluster_1_dic, actual_dic, labels)
    print("cluster 1 count: ", cluster_1_count)
    with open(os.path.join(data_dir, "cluster_2_predictions1.pkl"), "rb") as f:
        cluster_2_dic = pickle.load(f)
    cluster_2_count = evaluate_performance(cluster_2_dic, actual_dic, labels)
    print("cluster 2 count: ", cluster_2_count)

def main():
    #TODO: FILL IN feature_path
    dataset_path = "/home/yaatehr/programs/spatial_LDA/data/descriptors_test_1"
    # M = feature_extraction.create_feature_matrix(dataset_path)
    #CnnM = feature_extraction.create_feature_matrix_cnn(dataset_path)
    # feature_path = "/home/yaatehr/programs/spatial_LDA/data/features1.pkl"
    feature_path = "/home/yaatehr/programs/spatial_LDA/data/cnn_feature_matrix"
    with open(feature_path, "rb") as f:
        CnnM = pickle.load(f)
    lda = LDA2("", feature_path, n_topics = 3)  # Make the class
    lda_model = lda.off_the_shelf_LDA()  # Fit the sklearn LDA model
    predicted = {}
    img_files = os.listdir(dataset_path)
    # with open ("/home/yaatehr/programs/spatial_LDA/data/img_descriptors_dic1.pkl", "rb") as f:
    with open ("/home/yaatehr/programs/spatial_LDA/data/cnn_descriptors_dict01.pkl", "rb") as f:
        descriptor_dic = pickle.load(f)
    predicted_cluster = {}
    n_clusters = 80
    kmeans = KMeans(n_clusters=n_clusters)
    vstack = np.vstack([i for i in list(descriptor_dic.values()) if i is not None and i.shape[0] == n_keypoints])
    print(vstack.shape)
    kmeans.fit(vstack)
    num_files = 0
    for f in img_files:
        if num_files % 100 == 0:
            print(num_files)
        des = descriptor_dic[f]
        if des is None or des.shape[0] != n_keypoints:
            continue
        feature = feature_extraction.build_histogram(des, kmeans, n_clusters)
        predictions = lda_model.transform(np.reshape(feature, (1, feature.size)))
        predicted_class = np.argmax(predictions, axis=1)
        predicted_cluster[f] = predicted_class
        num_files += 1
    # with open ("/home/yaatehr/programs/spatial_LDA/data/predicted1.pkl", "wb") as f:
    with open ("/home/yaatehr/programs/spatial_LDA/data/cnn_predicted1.pkl", "wb") as f:
        pickle.dump(predicted_cluster, f)
    # Now we can predict!

def ryan_test():
    dataset_path = "/home/rmsander/Documents/6.867/test_dir/WelshCorgi.jpeg"
    img = cv.imread(dataset_path)
    M = feature_extraction.get_feature_vector(img)
    print(M)

if __name__ == "__main__":
    #evaluate_main()
    ryan_test()
