import numpy as np
import matplotlib as plt
from sklearn.cluster import KMeans, MiniBatchKMeans
from skimage.transform import rescale, resize
from dataset import ADE20K, get_single_loader, getDataRoot
from itertools import zip_longest
import os
from torchvision import transforms
import pickle
from pca import pca, featureNormalize
from collections import Counter
from tqdm import tqdm
from sklearn.decomposition import IncrementalPCA
from scipy import sparse
import matplotlib.pyplot as plt
# from feature_extraction import n_keypoints, n_cnn_keypoints, n_clusters,\
#  feature_model, cnn_num_layers_removed, num_most_common_labels_used

NUM_KMEANS_CLUSTERS = 100
data_root = os.path.join(os.path.dirname(__file__), '../data')

YAATEH_DATA_ROOT = "/Users/yaatehr/Programs/spatial_LDA/data/seg_data/images/training"
BOX_DATA_ROOT = "/home/yaatehr/programs/datasets/seg_data/images/training"
PICKLE_SAVE_RUN = True
def get_matrix_path(edge_len, nlabels):
    return os.path.join(data_root, "grayscale_img_matrix_%d_%d.pkl" % (edge_len, nlabels))


def stack_images_rows_with_pad(dataset,edge_len, nlabels):
    """
    If/when we use a transform this won't be necessary
    """
    path = get_matrix_path(edge_len, nlabels)

    print("checking baseline path: \n" , path)
    if not os.path.exists(path):
        list_of_images = []
        label_list = []

        dataset = get_single_loader(dataset, batch_size=1, shuffle_dataset=True)
        bar = tqdm(total= len(dataset))

        for step, (img, label) in enumerate(dataset):
            # if step > 100 or step > len(dataset) - 1:
            #     break
            list_of_images.append(img.flatten())
            label_list.append(label)
            if step % 50 == 0:
                bar.update(50)
        maxlen = max([len(x) for x in list_of_images])
        out = np.vstack([np.concatenate([b, np.zeros(maxlen-len(b))]) for b in list_of_images])
        print(out.shape)
        out = (out, label_list)
        with open(path, 'wb') as f:
            pickle.dump(out, f)
        return out
    else:
        with open(path, 'rb') as f:
            return pickle.load(f)


def resize_im_shape(img_shape, maxEdgeLen = 50):
    x,y = img_shape
    if x > y:
        maxEdge = x
    else:
        maxEdge = y

    scalefactor = maxEdgeLen/maxEdge
    remainderEdge = int(min(x,y) * scalefactor)
    if x > y:
        return maxEdgeLen, remainderEdge
    return remainderEdge, maxEdgeLen

def resize_im(im, edge_len):
    return resize(im, resize_im_shape(im.shape, maxEdgeLen=edge_len), anti_aliasing=False)
    

def createFeatureVectors(max_edge_len, n_keypoints):
    cnt = Counter()
    grayscaleDataset = ADE20K(grayscale=True, root=getDataRoot(), transform=lambda x: resize_im(x, max_edge_len), useStringLabels=True, randomSeed=49)#, numLabelsLoaded=10)

    #select most commoon label strings from tuples of (label, count)
    n_labels = 5
    mostCommonLabels =  list(map(lambda x: x[0], grayscaleDataset.counter.most_common(n_labels)))
    grayscaleDataset.selectSubset(mostCommonLabels, normalizeWeights=True)
    print(len(grayscaleDataset.counter))
    print("resized image size is: ", grayscaleDataset.__getitem__(0)[0].shape)
    # print("dataset len is: ", len(grayscaleDataset.image_paths))
    print("stacking and flattening images")

    stacked_images, label_list = stack_images_rows_with_pad(grayscaleDataset, max_edge_len, n_labels)
    # normalized_images = featureNormalize(stacked_images)[0]
    print("stacked im shape: " , stacked_images.shape)
    # U = pca.predict(stacked_images)
    pca_path = os.path.join(data_root, "pca_%d_clust_%d_edgelen_%d_keypoints.pkl" % (n_clust, max_edge_len, n_keypoints))
    print("for path:\n", pca_path)

    if os.path.exists(pca_path):
        U = pickle.load(open(pca_path, "rb"))
        print("Successfully loaded pca features")
    else:
        pca = IncrementalPCA(batch_size=79, n_components=n_keypoints)
        U = pca.fit_transform(stacked_images)
        pickle.dump(U, open(pca_path, "wb"))
        print("DUMPED PCA features")

    # U = pca(normalized_images)[0]


    print('fitting KMEANS')
    n_clust = len(grayscaleDataset.class_indices.keys())

    print("U shape: ", U.shape)

    kmeans_path = os.path.join(data_root, "kmeans_%d_clust_%d_edgelen_%d_keypoints.pkl" % (n_clust, max_edge_len, n_keypoints))
    print("for path:\n", kmeans_path)
    if os.path.exists(kmeans_path):
        kmeans = pickle.load(open(kmeans_path, "rb"))
        print("Successfully loaded kmeans")
    else:
        kmeans = MiniBatchKMeans(n_clusters=n_clust).fit(U)
        pickle.dump(kmeans, open(kmeans_path, "wb"))
        print("DUMPED Kmeans Model with")







    # print('stacking vectors KMEANS')


    # # for step, img in enumerate(stacked_images):
    # #     if step == 0:
    # #         vstack = img
    # #         continue
    # #     vstack = np.vstack((vstack, img))
    
    # # print(vstack)
    prediction = kmeans.predict(U)
    # print(prediction)
    path = os.path.join(data_root, "baseline_run_incremental_%d_%d.pkl" % (max_edge_len, n_keypoints))

    with open(path, "wb") as f:
        eval_tup = (prediction, label_list, kmeans, stacked_images.shape)
        pickle.dump(eval_tup, f)

    # percentage_plotted=.05
    # with open(path, "rb") as f:
    #     prediction, label_list, kmeans, vstackshape= pickle.load(f)
# "/Users/yaatehr/Programs/spatial_LDA/data/baselines top 5/baseline_5_clust_20_edgelen"
    plot_prefix =  "baseline_%d_clust_%d_edgelen_%d_kp" % (n_clust, max_edge_len, n_keypoints)
    label_subset = grayscaleDataset.class_indices.keys()
    label_to_predictions = {}
    for label in label_subset:
        labelIndices = grayscaleDataset.class_indices[label]
        histogram = np.zeros(n_clust)
        for i in labelIndices:
            f = grayscaleDataset.image_paths[i]
            # if np.random.random() < percentage_plotted:
                #Plot image histogram
            desc = U[i,:].reshape(1, -1)
            prediction = kmeans.predict(desc).item()
            histogram[prediction] += 1.0
        histogram /= len(labelIndices)

        label_to_predictions[label] = histogram


        plt.plot(histogram)
        plt.xlabel("unlabeled classes")
        plt.ylabel("predictions %")
        plt.title("PCA Kmeans prediction distribution for label %s" %label)
        axes = plt.gca()
        axes.set_xlim([0,n_clust-1])
        axes.set_ylim([0,1.0])

        plot_folder = os.path.join(data_root, plot_prefix)
        if not os.path.exists(plot_folder):
            os.makedirs(plot_folder)
        plt.savefig(os.path.join(plot_folder, "pca_kmeans_label%s.png"%(label, )))
        plt.close()
    pickle.dump(label_to_predictions, open(os.path.join(plot_folder, "label_to_pred.pkl"), "wb"))


def create_latex_table(n_labels, max_edge_len, n_keypoints):
    plot_prefix =  "baseline_%d_clust_%d_edgelen_%d_kp" % (n_labels, max_edge_len, n_keypoints)
    plot_folder = os.path.join(data_root + "/baselines top 5/", plot_prefix)
    print(plot_folder)
    label_to_predictions = pickle.load(open(os.path.join(plot_folder, "label_to_pred.pkl"), "rb"))

    latex_template = """
    \\begin{table}[H]
    \\begin{tabular}{%s}
    %s \\\\
    %s \\\\
    %s \\\\
    %s \\\\
    %s \\\\
    %s
    \\end{tabular}
    \\caption{Distribution over label predictions for PCA Kmeans clustering with %d clusters resized to a mix dimension of (%d,%d)}
    \\label{Tab:baseline%dclust%dlen}
    \\end{table}
    """ % (
        "l"*(n_labels+1),
        " & Clust. ".join(["Label"] + [str(i) for i in range(n_labels)]),
        *[" & ".join([label] + np.around(label_to_predictions[label], decimals=3).astype(str).tolist()) for label in label_to_predictions ],
        n_labels,
        max_edge_len,
        max_edge_len,
        n_labels,
        max_edge_len,
    )
    print(latex_template)


for i in range(300, 500, 20):
    for j in range(5, 105, 10):
        createFeatureVectors(i, j)
        # create_latex_table(5, i, j)



