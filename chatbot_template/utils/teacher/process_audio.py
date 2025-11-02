from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np

from chatbot_template.config.general_config import N_MELS, N_MFCC, SAMPLING_RATE
from chatbot_template.utils.enums import AudioFeatureType


class AudioProcessor:
    """Audio processor class for loading and transforming audio signals."""

    def __init__(self, sampling_rate: int = SAMPLING_RATE) -> None:
        """
        Initialize the audio processor.

        Parameters
        ----------
        sampling_rate : int
            Sampling rate used when loading audio files.
        """
        self.sampling_rate: int = sampling_rate

    # ----------------------------------------------------------

    def load_audio(self, file_path: str | Path) -> np.ndarray:
        """
        Load an audio file and convert it to mono.

        Parameters
        ----------
        file_path : str or Path
            Path to the audio file.

        Returns
        -------
        audio : np.ndarray
            1D numpy array containing the audio samples normalized to [-1, 1].
        """
        audio, _ = librosa.load(file_path, sr=self.sampling_rate, mono=True)
        return audio

    # ----------------------------------------------------------

    def process(
        self,
        file_path: str | Path,
        feature_type: AudioFeatureType,
        save_path: str | Path | None = None,
        include_deltas: bool = False,
    ) -> np.ndarray:
        """
        Process an audio file into a specific representation.

        Parameters
        ----------
        file_path : str or Path
            Path to the input audio file.
        feature_type : AudioFeatureType
            Desired feature representation (RAW, STFT, MEL, or MFCC).
        save_path : str or Path, optional
            If provided, the resulting array will be saved as a `.npy` file.
        include_deltas : bool, default=False
            If True and the feature type is MFCC,
            includes delta and delta-delta features.

        Returns
        -------
        data : np.ndarray
            The computed feature representation:
            - RAW  → shape (n_samples,)
            - STFT → shape (n_freq_bins, n_frames)
            - MEL  → shape (n_mels, n_frames)
            - MFCC → shape (n_features, n_frames)
        """
        y: np.ndarray = self.load_audio(file_path)

        if feature_type == AudioFeatureType.RAW:
            data: np.ndarray = y

        elif feature_type == AudioFeatureType.STFT:
            stft: np.ndarray = librosa.stft(y)
            data = np.abs(stft)

        elif feature_type == AudioFeatureType.MEL:
            mel: np.ndarray = librosa.feature.melspectrogram(
                y=y, sr=self.sampling_rate, n_mels=N_MELS
            )
            data = librosa.power_to_db(mel, ref=np.max)

        elif feature_type == AudioFeatureType.MFCC:
            mfcc: np.ndarray = librosa.feature.mfcc(
                y=y, sr=self.sampling_rate, n_mfcc=N_MFCC
            )
            if include_deltas:
                delta: np.ndarray = librosa.feature.delta(mfcc)
                delta2: np.ndarray = librosa.feature.delta(mfcc, order=2)
                data = np.vstack([mfcc, delta, delta2])
            else:
                data = mfcc
        else:
            raise ValueError(f"Unknown feature type: {feature_type}")

        if save_path is not None:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(save_path, data)

        return data
