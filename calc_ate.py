# Import all dependencies
import os
import csv
import numpy as np
import argparse
from functools import partial
from itertools import product

from multiprocessing import Pool
from matplotlib import pyplot as plt
import geopandas as gpd
from scipy.spatial.distance import hamming as hamming_loss

import Datasets
from distance_metrics import (
    weighted_hamming_wrapper,
    jensenshannon_wrapper,
    kl_divergence_wrapper,
    jaccard_distance_wrapper,
)


def main(args):
    # Load images
    dataset = Datasets.load("pm_train_only")
    # Load traversal path
    df = load_traversal_path(args.traversal_data)

    ##################
    #  Set up parameters to checkout
    ##################

    results_dir = os.path.dirname(args.results_path)
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # This is the minimum distance from which to retrieve
    # the nearest neighbors. We do not want to get
    # neighbors that are closer to a specific distance, as
    # these neighbors are more directly influenced by
    # the covariates.
    neighborhood_min_dist = [args.neighborhood_min_dist]

    # Number of neighbors to average over.
    num_neighbors = [5, 10, 15, 20, 25]

    # Treatment/control values
    distance = [20, 40, 80]  # box of 2*distance x 2*distance in the center
    treatment_idx = 0  # id used for concrete (this should not change)
    control_idx = 2  # id used for trees (this should not change)
    treatment_pctg = [0.6, 0.7, 0.8, 0.9]  # percentage covered by treatment
    control_pctg = [0.6, 0.7, 0.8, 0.9]  # percentage covered by control
    match_radius = [0.5, 1, 1.5, 2]

    # Get the total number of trials to run:
    num_trials = (
        len(neighborhood_min_dist)
        * len(num_neighbors)
        * len(distance)
        * len(treatment_pctg)
        * len(control_pctg)
        * len(match_radius)
    )
    print(f"Total number of trials: {num_trials}")
    counter = 1

    # Create to store results
    with open(args.results_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",")

        # Write the header
        writer.writerow(
            [
                "Neighborhood min dist",
                "Num neighbors",
                "Treatment/Control Radius",
                "Treatment %",
                "Control %",
                "Match Radius",
                "Treatment Count",
                "Control Count",
                "ATE",
                "TE Std",
                "Average Match Distance",
            ]
        )

    # Iterate over the prognostic dependent variables
    for n_min_dist, nn in product(neighborhood_min_dist, num_neighbors):
        print(f"Neighborhood min dist: {n_min_dist}, Num neighbors: {nn}")
        # Calculate the match values
        match_values = calc_match_values(dataset, df, n_min_dist, nn)
        for dist, t_pctg, c_pctg, match_rad in product(
            distance, treatment_pctg, control_pctg, match_radius
        ):
            # Get the treatment and controls
            print(f"Dist: {dist}, Treatment %: {t_pctg}, Control %: {c_pctg}")
            print(f"Running trial {counter} of {num_trials}")
            treatment, control = create_treatment_and_control_groups(
                dist,
                treatment_idx,
                control_idx,
                t_pctg,
                c_pctg,
                match_values,
                dataset,
            )

            print("\tPre-matching treatment size: ", len(treatment))
            print("\tPre-matching control size: ", len(control))

            treatment_vals, control_vals, match_distances = get_matches(
                treatment, control, match_rad, args.distance_metric
            )

            ate = np.mean(treatment_vals) - np.mean(control_vals)
            ate_std = np.std(np.array(treatment_vals) - np.array(control_vals))
            # Record the results
            with open(args.results_path, "a", newline="") as f:
                writer = csv.writer(f, delimiter=",")
                writer.writerow(
                    [
                        n_min_dist,
                        nn,
                        dist,
                        t_pctg,
                        c_pctg,
                        match_rad,
                        len(treatment_vals),
                        len(control_vals),
                        ate,
                        ate_std,
                        np.mean(match_distances),
                    ]
                )
            print("\tATE: {ate}")
            counter += 1


def get_matches(treatment, control, match_radius, distance_metric):
    """This function will return the treatment and control values that are within a certain distance of each other"""
    # Set up the treatment and control values
    treatment_vals = []
    control_vals = []
    match_distance = []  # Record the average match distance

    for t_img, _, t_temp, match_val in treatment:
        # Create control function and implement as a filter
        get_control_pool = partial(
            filter_control_matches_by_radius, match_radius, match_val
        )
        valid_controls = list(filter(get_control_pool, control))

        if len(valid_controls) == 0:
            continue
        else:
            treatment_vals.append(t_temp)

        # Get the closest control via the distance metric
        control_val, control_dist = get_closest_control(
            valid_controls, t_img, distance_metric
        )
        control_vals.append(control_val)
        match_distance.append(control_dist)
    return treatment_vals, control_vals, match_distance


def get_closest_control(control_pool, t_img, distance_metric):
    """This function will calculate the closest control based on the distance used."""
    best_dist = np.inf
    best_control = None

    # TODO -- add more distance metrics here
    if distance_metric == "hamming":
        distance_metric = hamming_loss
    elif distance_metric == "jaccard":
        distance_metric = jaccard_distance_wrapper
    elif distance_metric == "weighted_hamming":
        distance_metric = weighted_hamming_wrapper
    elif distance_metric == "kl_divergence":
        distance_metric = kl_divergence_wrapper
    elif distance_metric == "jensenshannon":
        distance_metric = jensenshannon_wrapper
    else:
        raise ValueError(f"Distance metric {distance_metric} not recognized.")

    for c_img, _, c_temp, _ in control_pool:
        sim = distance_metric(t_img.flatten(), c_img.flatten())

        if sim < best_dist:
            best_dist = sim
            best_control = c_temp

    return best_control, best_dist


def filter_control_matches_by_radius(radius, treatment_val, control_val):
    """This is a function that will return true if the treatment and control
    are within a certain distance of each other"""
    if abs(treatment_val - control_val[3]) < radius:
        return True
    return False


def create_treatment_and_control_groups(
    dist,
    treatment_idx,
    control_idx,
    treatment_pctg,
    control_pctg,
    match_values,
    dataset,
):
    treatment_group = []
    control_group = []

    # Set a few variables
    w, h, _ = dataset[0][0].shape

    # Look at each image and file into the categories
    for (img, file_name, label), mv in zip(dataset, match_values):
        # Look at pixels in the middle of the image
        area = img[w // 2 - dist : w // 2 + dist, h // 2 - dist : h // 2 + dist, :]

        if area[:, :, treatment_idx].mean() > treatment_pctg:
            treatment_group.append((img, file_name, label, mv))

        if area[:, :, control_idx].mean() > control_pctg:
            control_group.append((img, file_name, label, mv))

    return treatment_group, control_group


def calc_match_values(dataset, df, n_min_dist, nn):
    match_values = []

    # Iterate over the dataset to calculate the match values
    for i, (_, file_name, _) in enumerate(dataset):
        # Read off the point from the file name
        point_id = int(file_name.split("_")[-1].split(".")[0])

        # Get the point
        point = df.iloc[point_id]

        # Calculate the distance close to that point id
        df["dist"] = np.sqrt(
            (df.geometry.x - point.geometry.x) ** 2
            + (df.geometry.y - point.geometry.y) ** 2
        )

        # Calculate the prog score
        sort_arr = df[
            df["dist"] > n_min_dist
        ]  # Must be at least 600 meters away (to be far enough away from the point)
        prog_score = sort_arr.sort_values("dist")[0:nn]["temp_f"].mean()

        # Append value
        match_values.append(prog_score)

    return np.array(match_values)


def load_traversal_path(data_path):
    """Read the file and convert to mercator projection"""
    df = gpd.read_file(data_path)
    # Convert to meters
    return df.to_crs(epsg=3857)


if __name__ == "__main__":
    # Set up arguments to be passed via script
    parser = argparse.ArgumentParser(description="Calculate ATE")

    # Argument for where to load data
    parser.add_argument(
        "--traversal_data",
        type=str,
        default="/datacommons/carlsonlab/zdc6/uhi/data/traverses/pm_trav.shp",
    )
    # Argument for where to dump results
    parser.add_argument("--results_path", type=str, default="./ate_results.csv")
    # Argument for distance metric
    parser.add_argument("--distance_metric", type=str, default="hamming")

    parser.add_argument("--neighborhood_min_dist", type=int, default=550)

    # Retrieve the arguments
    args = parser.parse_args()

    main(args)
