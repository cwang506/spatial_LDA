"""A pre-processing script for cropping objects of interest in images to
their detected bounding boxes."""

# Native Python imports
import os

# External package imports
import numpy as np
import cv2 as cv
import csv


def parse_bounding_csv(path_to_csv):
    """Parses the boundary box csv file. Gets information such as image ID,
    label name, boundaries (in percentages). Returns a dictionary of
    imageId:[(label, boundary)]"""
    parsed = {}
    with open(path_to_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                image_id = row[0]
                boundary = {}
                boundary["xMin"] = row[4]
                boundary["xMax"] = row[5]
                boundary["yMin"] = row[6]
                boundary["yMax"] = row[7]
                label = row[2]
                if image_id not in parsed:
                    parsed[image_id] = [(label, boundary)]
                else:
                    lis = parsed[image_id]
                    lis.append((label, boundary))
                    parsed[image_id] = lis
                line_count += 1
        print(f'Processed {line_count} lines.')
    return parsed


def parse_label_to_class_names(path_to_csv):
    """Returns a dictionary of label:class name"""
    parsed = {}
    with open(path_to_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            parsed[row[0]] = row[1]
            line_count += 1
        print(f'Processed {line_count} lines.')
    return parsed

def crop_object(f_img, lb_pairs,
                out_root_dir="/home/yaatehr/programs/spatial_LDA/data"
                             "/cropped_test_0"):
    """Function for cropping a single object in a single image, and saves
    the cropped image into the out_dir output directory."""
    # Load image and get shape
    A = cv.imread(f_img)
    m, n, c = A.shape

    # Iterate over all labels in the image
    for label, lb_pair in zip(labels, lb_pairs):
        # Get label and boundary
        label, boundary = lb_pair

        # Convert min/max values from percentages to pixels
        xmin = n * boundary["xMin"]
        xmax = n * boundary["xMax"]
        ymin = m * boundary["yMin"]
        ymax = m * boundary["yMax"]

        # Crop image to object values over bounding box with all channels
        A_crop = A[ymin:ymax, xmin:xmax, :]

        # Get output directory using class label
        out_root_dir = out_dir

        # Save image
        cv.imwrite(os.path.join(os.getcwd(), out_dir), A_crop)


def sort_objects_by_class(img_dir, label_dir, csv_path):
    """Main function for cropping our objects of interest into their respective
    classes."""
    # Get dictionary of parsed values
    parsed = parse_bounding_csv(csv_path)

    # Get image ids from parsed data
    ids = list(parsed.keys())
    counter = 0  # For printing

    # Iterate over all images via ids
    for id in ids:
        print("Iterated over {} images".format(counter))
        crop_object(parsed[id])  # Crop and save image objects by class
        counter += 1
