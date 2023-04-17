from scipy.spatial.distance import hamming as hamming_loss
from scipy.spatial.distance import jensenshannon
from scipy.stats import entropy
from sklearn.metrics import jaccard_score
import numpy as np

def weighted_hamming_wrapper(x_input, y_input, n = 256):
    n = 256
    center = n // 2

    # Create 1D arrays representing the x and y coordinates
    x = np.arange(n)
    y = np.arange(n)
    
    # Use meshgrid to create 2D arrays representing the x and y distances from the center
    x_distance, y_distance = np.meshgrid(x - center, y - center, indexing='ij')

    # Use linalg.norm to create a 2D array representing the Euclidean distances from the center
    distance = np.linalg.norm(np.stack((x_distance, y_distance), axis=-1), axis=-1)

    # Calculate the weight of each pixel using the formula 1 / (1 + distance**2)
    weight_matrix = 1 / (1 + distance**2)

    # Stack the weight matrix along the third axis to create a 256 x 256 x 4 array
    stacked_weights = np.stack([weight_matrix] * 4, axis=-1)
    
    return hamming_loss(x_input, y_input, w=stacked_weights.flatten())

def jensenshannon_wrapper(x, y):
#     land_use_1 = x.reshape(4, 256, 256)
#     land_use_2 = y.reshape(4, 256, 256)
    
#     # Compute the probability distributions by dividing each pixel value by the total number of pixels
#     dist1 = land_use_1 / land_use_1.sum(axis=(0, 1, 2), keepdims=True)
#     dist2 = land_use_2 / land_use_2.sum(axis=(0, 1, 2), keepdims=True)

#     # Flatten the distributions to 1D arrays for use with the JSD metric
#     flat_dist1 = dist1.reshape(-1)
#     flat_dist2 = dist2.reshape(-1)

    x = x.reshape(4, 256, 256)
    y = y.reshape(4, 256, 256)

    # Convert one-hot encoded vectors to probability distributions
    x_probs = np.apply_along_axis(lambda a: np.exp(a) / np.sum(np.exp(a)), axis=2, arr=x)
    y_probs = np.apply_along_axis(lambda a: np.exp(a) / np.sum(np.exp(a)), axis=2, arr=y)
    
    return jensenshannon(x_probs.flatten(), y_probs.flatten())

def kl_divergence_wrapper(x,y):
    t_img = x.reshape((256,256,4))
    c_img = y.reshape((256,256,4))

    t_dist = np.mean(t_img, axis=(0, 1))
    c_dist = np.mean(c_img, axis=(0, 1))
    
    return entropy(t_dist, c_dist)

def jaccard_distance_wrapper(x,y):
    #Code is exactly the same as sklearn, can choose whatever is fastest
    #distance_metric = lambda x, y: 1 - (np.sum(np.logical_and(x, y)) / np.sum(np.logical_or(x, y)))
    
    return 1 - jaccard_score(x, y)