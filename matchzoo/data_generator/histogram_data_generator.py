"""Data generator with matching histogram."""

import numpy as np

from matchzoo.processor_units import MatchingHistogramUnit
from matchzoo.data_pack import DataPack
from matchzoo.data_generator import DataGenerator
from matchzoo.data_generator import PairDataGenerator


def trunc_text(text: list, length: list) -> list:
    """Truncating the input text according to the input length."""
    return [row[:length[idx]] for idx, row in enumerate(text)]


def match_histogram_generator(x: dict,
                              match_hist_unit: MatchingHistogramUnit) -> list:
    """
    Generator the matching hisogram for input.

    :param x: The input `dict`.
    :return: The matching histogram.
    """
    match_hist = []
    text_left = trunc_text(x['text_left'].tolist(), x['length_left'].tolist())
    text_right = trunc_text(x['text_right'].tolist(),
                            x['length_right'].tolist())
    for pair in zip(text_left, text_right):
        match_hist.append(match_hist_unit.transform(list(pair)))
    return match_hist


class HistogramDataGenerator(DataGenerator):
    """
    Generate data with matching histogram.

    :param data_pack: The input data pack.
    :param embedding: The embedding matrix used to generator match histogram.
    :param hist_bins: The number of bin size of the histogram.
    :param hist_mode: The mode of the :class:`MatchingHistogramUnit`, one of
                     `CH`, `NH`, and `LCH`.
    :param batch_size: The batch size.
    :param shuffle: Boolean, whether to shuffle the data while generating a
                    batch.

    Examples:
        >>> import matchzoo as mz
        >>> raw_data = mz.datasets.toy.load_data()
        >>> preprocessor = mz.preprocessors.BasicPreprocessor()
        >>> processed_data = preprocessor.fit_transform(raw_data)
        >>> raw_embedding = mz.embedding.load_from_file(
        ...     mz.datasets.embeddings.EMBED_10_GLOVE
        ... )
        >>> embedding_matrix = raw_embedding.build_matrix(
        ...     preprocessor.context['vocab_unit'].state['term_index']
        ... )
        >>> data_generator = HistogramDataGenerator(processed_data,
        ...     embedding_matrix, 3, 'CH', batch_size=3, shuffle=False
        ... )
        >>> x, y = data_generator[-1]
        >>> type(x)
        <class 'dict'>
        >>> x.keys()
        dict_keys(['id_left', 'text_left', 'length_left', 'id_right', \
'text_right', 'length_right', 'match_histogram'])
        >>> type(x['match_histogram'])
        <class 'numpy.ndarray'>
        >>> type(y)
        <class 'numpy.ndarray'>

    """

    def __init__(self,
                 data_pack: DataPack,
                 embedding: np.ndarray,
                 hist_bins: int = 30,
                 hist_mode: str = 'CH',
                 batch_size: int = 32,
                 shuffle: bool = True):
        """:class:`HistogramDataGenerator` constructor."""
        self._match_hist_unit = MatchingHistogramUnit(hist_bins=hist_bins,
                                                      embedding=embedding,
                                                      normalize=True,
                                                      mode=hist_mode)
        # Here the super().__init_ must be after the self._data_pack
        super().__init__(data_pack, batch_size, shuffle)

    def _get_batch_of_transformed_samples(self, indices: np.array):
        """Get a batch of instances."""
        x, y = super()._get_batch_of_transformed_samples(indices)
        x['match_histogram'] = np.array(
            match_histogram_generator(x, self._match_hist_unit))
        return (x, y)


class HistogramPairDataGenerator(PairDataGenerator):
    """
    Generate pair-wise data with matching histogram.

    :param data_pack: The input data pack.
    :param embedding: The embedding matrix used to generator match histogram.
    :param hist_bins: The number of bin size of the histogram.
    :param hist_mode: The mode of the :class:`MatchingHistogramUnit`, one of
                     `CH`, `NH`, and `LCH`.
    :param batch_size: The batch size.
    :param shuffle: Boolean, whether to shuffle the data while generating a
                    batch.

    Examples:
        >>> np.random.seed(111)
        >>> import matchzoo as mz
        >>> raw_data = mz.datasets.toy.load_data()
        >>> preprocessor = mz.preprocessors.BasicPreprocessor()
        >>> processed_data = preprocessor.fit_transform(raw_data)
        >>> raw_embedding = mz.embedding.load_from_file(
        ...     mz.datasets.embeddings.EMBED_10_GLOVE
        ... )
        >>> embedding_matrix = raw_embedding.build_matrix(
        ...     preprocessor.context['vocab_unit'].state['term_index']
        ... )
        >>> data_generator = HistogramPairDataGenerator(processed_data,
        ...     embedding_matrix, 3, 'CH', 1, 1, 3, False)
        >>> len(data_generator)
        2
        >>> x, y = data_generator[0]
        >>> type(x)
        <class 'dict'>
        >>> x.keys()
        dict_keys(['id_left', 'text_left', 'length_left', 'id_right', \
'text_right', 'length_right', 'match_histogram'])
        >>> type(x['match_histogram'])
        <class 'numpy.ndarray'>
        >>> type(y)
        <class 'numpy.ndarray'>

    """

    def __init__(self,
                 data_pack: DataPack,
                 embedding: np.ndarray,
                 hist_bins: int = 30,
                 hist_mode: str = 'CH',
                 num_dup: int = 1,
                 num_neg: int = 1,
                 batch_size: int = 32,
                 shuffle: bool = True):
        """:class:`DPoolPairDataGenerator` constructor.

        """
        self._match_hist_unit = MatchingHistogramUnit(hist_bins=hist_bins,
                                                      embedding=embedding,
                                                      normalize=True,
                                                      mode=hist_mode)
        # Here the super().__init__ must be after the self._data_pack
        super().__init__(data_pack, num_dup, num_neg, batch_size, shuffle)

    def _get_batch_of_transformed_samples(self, indices: np.array):
        """Get a batch of paired instances."""
        x, y = super()._get_batch_of_transformed_samples(indices)
        x['match_histogram'] = np.array(
            match_histogram_generator(x, self._match_hist_unit))
        return (x, y)
