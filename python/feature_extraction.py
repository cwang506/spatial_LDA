import cv2 as cv
import numpy as np
import os
from sklearn.cluster import MiniBatchKMeans, KMeans
from sklearn.neural_network import MLPClassifier
from sklearn.datasets import make_multilabel_classification
import pickle

n_keypoints = 100 #hyperparameter, need to tune

def get_feature_vector(img):
    # Get keypoints and feature descriptors
    sift = cv.xfeatures2d_SIFT.create(n_keypoints)
    kp, des = sift.detectAndCompute(img, None)
    return kp, des


def build_histogram(descriptor_list, cluster_alg, n_clusters):
    """Helper function/sub-routine that uses a fitted clustering algorithm
    and a descriptor list for an image to a histogram."""
    histogram = np.zeros(n_clusters)
    cluster_result = cluster_alg.predict(descriptor_list)
    for i in cluster_result:
        histogram[i] += 1.0
        return histogram


def create_feature_matrix(img_path, n_clusters=50):
    """Main function for creating a matrix of size N_images x n_clusters
    using SIFT and histogramming of the descriptors by a clustering
    algorithm."""
    # Make clustering algorithm
    kmeans = KMeans(n_clusters=n_clusters)
    img_files = os.listdir(img_path)
    # print(img_files)
    print(len(img_files))
    with open("/home/yaatehr/programs/spatial_LDA/data/img_descriptors_dic.pkl","rb") as f:

        descriptor_list_dic = pickle.load(f)
    # for f in img_files:
    #     A = cv.imread(os.path.join(img_path, f)) # read image
    #     _, des = get_feature_vector(A)
    #     descriptor_list_dic[f]= des
    # with open("/home/yaatehr/programs/spatial_LDA/data/img_descriptors_dic.pkl", "wb") as f:
    #     pickle.dump(descriptor_list_dic, f)
    print([i.shape for i in list(descriptor_list_dic.values()) if i is not None and i.shape[0] == n_keypoints])
    vstack = np.vstack([i for i in list(descriptor_list_dic.values()) if i is not None and i.shape[0] == n_keypoints])
    print(vstack.shape)
    kmeans.fit(vstack)

    # Get image files
    M = []
    num_files = 0
    for f in img_files:  # Iterate over all image files
        if num_files % 100 == 0:
            print(num_files+" files processed")
        des = descriptor_list_dic[f]  # Get keypoints/descriptors from SIFT
        if des is None or des.shape[0] != n_keypoints:
            continue
        histogram = build_histogram(des, kmeans, n_clusters)
        
        M.append(histogram)  # Append to output matrix
        num_files += 1
    print(M.shape)
    return M

def main():
    dataset_path = "/home/yaatehr/programs/spatial_LDA/data/descriptors_test_0"
    M = create_feature_matrix(dataset_path)



if __name__ == "__main__":
    main()
