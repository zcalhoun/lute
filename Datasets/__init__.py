def load(name):
    from .base import OneHotImages

    if name == "base":
        # Load the train
        train = OneHotImages("/datacommons/carlsonlab/zdc6/cs590/land_use/train")
        test = OneHotImages("/datacommons/carlsonlab/zdc6/cs590/land_use/test")

        return train, test
