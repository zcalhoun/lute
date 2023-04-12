def load(name):
    from .base import OneHotImages

    if name == "base":
        # Load the train
        train = OneHotImages("/datacommons/carlsonlab/zdc6/cs590/land_use/train")
        test = OneHotImages("/datacommons/carlsonlab/zdc6/cs590/land_use/test")

        return train, test
    elif name == "pm_train_only":
        from matching import MatchingDataset

        # We only need the training data
        train = MatchingDataset("/datacommons/carlsonlab/zdc6/cs590/land_use/train")
        train_data = train.get_data_parallel()

        return train_data
