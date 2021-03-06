#!/usr/bin/env python

"""
Convert the Kaldi MFCC features to Numpy format and normalize.

Author: Herman Kamper
Contact: kamperh@gmail.com
Date: 2017
"""

from datetime import datetime
from os import path
import numpy as np
import os
import PIL.Image as Image
import sys

sys.path.append(path.join("..", "tflego", "utils"))

from data_io import read_kaldi_ark_from_scp
from get_kaldi_fbank import get_flickr8k_train_test_dev
import plotting

flickr8k_text_base_dir = "/share/data/lang/users/kamperh/flickr_multimod/Flickr8k_text/"
mfcc_dir = path.join("..", "kaldi_features", "mfcc")
scp_fn = path.join(mfcc_dir, "mfcc_cmnv_dd_full_vad.scp")
# scp_fn = "tmp3.scp"
data_dir = path.join("data", "mfcc_cmvn_dd_vad")


def main():

    if not path.isdir(data_dir):
        os.mkdir(data_dir)

    print datetime.now()
    print "Reading:", scp_fn
    features_dict = read_kaldi_ark_from_scp(scp_fn, ark_base_dir=path.split(mfcc_dir)[0])
    print datetime.now()
    print "No. utterances:", len(features_dict)

    plot_fn = path.join(data_dir, "original_eg.png")
    print "Writing:", plot_fn
    first_utt = features_dict.keys()[0]
    image = Image.fromarray(plotting.array_to_pixels(features_dict[first_utt]))
    image.save(plot_fn)

    print features_dict[first_utt]
    print 

    # Global mean and variance normalization over all data
    all_features = np.vstack(features_dict.values())
    mean = np.mean(all_features)
    std = np.std(all_features)
    for utt in features_dict:
        features_dict[utt] = (features_dict[utt] - mean) / std
    plot_fn = path.join(data_dir, "normalized_eg.png")
    print "Writing:", plot_fn
    image = Image.fromarray(plotting.array_to_pixels(features_dict[first_utt]))
    image.save(plot_fn)

    # Train, dev, test split
    set_dict = get_flickr8k_train_test_dev()

    # Train, dev, test dictionaries
    train_dict = {}
    dev_dict = {}
    test_dict = {}
    for utt in features_dict:
        utt_base = utt[4:-2]
        if utt_base in set_dict["train"]:
            train_dict[utt] = features_dict[utt]
        elif utt_base in set_dict["dev"]:
            dev_dict[utt] = features_dict[utt]
        elif utt_base in set_dict["test"]:
            test_dict[utt] = features_dict[utt]
        else:
            assert False
    print "No. train utterances:", len(train_dict)
    print "No. test utterances:", len(test_dict)
    print "No. dev utterances:", len(dev_dict)

    # Write train, dev, test Numpy archives
    train_fn = path.join(data_dir, "train.npz")
    dev_fn = path.join(data_dir, "dev.npz")
    test_fn = path.join(data_dir, "test.npz")
    print "Writing:", train_fn
    np.savez_compressed(train_fn, **train_dict)
    print "Writing:", dev_fn
    np.savez_compressed(dev_fn, **dev_dict)
    print "Writing:", test_fn
    np.savez_compressed(test_fn, **test_dict)

    plot_fn = path.join(data_dir, "train_eg.png")
    print "Writing:", plot_fn
    image = Image.fromarray(plotting.array_to_pixels(train_dict[sorted(train_dict.keys())[0]]))
    image.save(plot_fn)
    print datetime.now()


if __name__ == "__main__":
    main()
