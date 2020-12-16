import numpy as np
import pandas as pd
from sklearn.feature_selection import f_classif, f_regression


class SelectKBest:
    """Class for finding K highest scoring features among the set of all features. Takes a feature and finds its correlation with the
    target label using a scoring function.

    Scoring functions include:

    1. f_regression
    2. mutual_info_regression
    3. f_classif
    4. mutual_info_classif
    5. chi2

    All scoring functions are provided in sklearn.feature_selection

    Private Methods
    ---------------

    __get_mask() : Generates mask that contains features to be selected

    Public Methods
    --------------

    fit() : Generates scores and pvalues by fitting the scoring function over the dataset

    transform() : Uses the mask to select the k best features

    fit_transform() : Performs fit() then transform()

    """

    def __init__(self, score_func=None, k=10):
        """Constructor

        Parameters
        ----------

        score_func : callable, default=None. Function taking two arrays X and y, and returning a pair of arrays
                     (scores, pvalues) or a single array with scores. score_func is provided from sklearn.feature_selection

        k : int , default=10. Number of top features to select.

        """

        self.k = k
        self.score_func = score_func
        self.scores = None
        self.pvalues = None

    def __get_mask(self):
        """Function to generate mask for selecting features. Uses the scores generated by the scoring function to select the k
        highest scoring features.

        Returns
        -------

        mask : ndarray of type=bool, shape=(n_features,). Boolean mask of features to be selected.

        """
        if self.k == 0:
            return np.zeros(self.scores.shape, dtype=bool)

        if self.scores is None:
            raise ValueError(
                f"self.scores is None. Please fit the estimator before calling transform."
            )

        mask = np.zeros(self.scores.shape, dtype=bool)
        # select k highest scored features
        mask[np.argsort(self.scores, kind="stable")[-self.k :]] = 1
        return mask

    def fit(self, X, y):
        """Function that fits the scoring function over (X,y) and generates the scores and pvalues for all features with the
        target label. If no scoring function is passed, then defaults to f_classify or f_regression based on the predictive
        problem.

        Parameters
        ----------

        X : pd.core.frame.DataFrame of shape (n_samples, n_features). The training input samples.

        y : pd.core.series.Series of shape (n_samples,). The target values (class labels in classification, real numbers in
            regression).

        Returns
        -------
        self : object

        """

        if not isinstance(X, pd.core.frame.DataFrame):
            raise TypeError(
                f"Feature dataframe is not a valid dataframe.\nExpected object type: pandas.core.frame.DataFrame"
            )

        if not isinstance(y, pd.core.series.Series):
            raise TypeError(
                f"Target column is not a valid series.\nExpected object type: pandas.core.series.Series"
            )

        if self.score_func is None:
            if y.nunique() <= 15:
                self.score_func = f_classif
            else:
                self.score_func = f_regression

        if not callable(self.score_func):
            raise TypeError(
                f"The score function should be a callable, {self.score_func} of type ({type(self.score_func)}) was passed."
            )

        score_func_ret = self.score_func(X, y)
        if isinstance(score_func_ret, (list, tuple)):
            self.scores, self.pvalues = score_func_ret
            self.pvalues = np.asarray(self.pvalues)
        else:
            self.scores = score_func_ret
            self.pvalues = None

        self.scores = np.asarray(self.scores)

        return self

    def transform(self, X):
        """Function to reduce X to the selected features. Returns dataframe of shape (n_samples,k)

        Parameters
        ----------

        X : pd.core.frame.DataFrame of shape (n_samples, n_features). The input samples.

        Returns
        -------

        X_new : array of shape (n_samples, k). The input samples with only the selected features.

        """

        mask = self.__get_mask()
        if not mask.any():
            raise ValueError(
                f"No features were selected: either the data is too noisy or the selection test too strict."
            )

        if len(mask) != X.shape[1]:
            raise ValueError("X has a different shape than during fitting.")

        return X.iloc[:, mask]

    def fit_transform(self, X, y):
        """Does fit() and transform() in single step

        Parameters
        ----------

        X : pd.core.frame.DataFrame of shape (n_samples, n_features). The training input samples.

        y : pd.core.series.Series of shape (n_samples,). The target values (class labels in classification, real numbers in
            regression).

        Returns
        -------

        X_new : array of shape (n_samples, k). The input samples with only the selected features.

        """
        return self.fit(X, y).transform(X)
