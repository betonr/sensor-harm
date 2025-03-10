#
# This file is part of Sensor Harmonization
# Copyright (C) 2020-2021 INPE.
#
# Sensor Harmonization (Landsat-8 and Sentinel-2) is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Sensor Harmonization of Sentinel 2A/2B data products."""

# Python Native
import logging
import os
import re
from pathlib import Path
from typing import Optional

# 3rdparty
import s2angs

# sensor-harm
from .harmonization_model import process_NBAR


def sentinel_harmonize_SAFE(safel2a: str, target_dir: Optional[str] = None, apply_bandpass: bool = True):
    """Prepare Sentinel-2 NBAR from Sen2cor.

    Args:
        safel2a (str): path to SAFEL2A directory.
        target_dir (str): path to output result images.
        apply_bandpass - Apply the band pass processing. Default is True.

    Returns:
        str: path to folder containing result images.
    """
    # Generating Angle bands
    sz_path, sa_path, vz_path, va_path = s2angs.gen_s2_ang(str(safel2a))

    if target_dir is None:
        target_dir = safel2a.joinpath('GRANULE', os.listdir(safel2a.joinpath('GRANULE'))[0], 'HARMONIZED_DATA/')
    target_dir.mkdir(parents=True, exist_ok=True)

    logging.info('Harmonization ...')
    # Sentinel-2 data set
    satsen = safel2a.name[:3]
    logging.info('SatSen: {}'.format(satsen))
    scene_id = Path(safel2a).stem

    img_dir = safel2a.joinpath('GRANULE', os.listdir(safel2a.joinpath('GRANULE'))[0], 'IMG_DATA/R10m/')
    bands10m = ['B02', 'B03', 'B04', 'B08']
    process_NBAR(img_dir, scene_id, bands10m, sz_path, sa_path, vz_path, va_path, satsen, target_dir, apply_bandpass)

    img_dir = safel2a.joinpath('GRANULE', os.listdir(safel2a.joinpath('GRANULE'))[0], 'IMG_DATA/R20m/')
    bands20m = ['B8A', 'B11', 'B12']
    process_NBAR(img_dir, scene_id, bands20m, sz_path, sa_path, vz_path, va_path, satsen, target_dir, apply_bandpass)

    # COPY quality band
    pattern = re.compile('.*SCL.*')
    img_list = img_dir.glob('**/*.jp2')
    qa_filepath = Path(list(item for item in img_list if pattern.match(str(item)))[0])
    # Convert jp2 to tiff
    os.system('gdal_translate -of Gtiff ' + str(qa_filepath) + ' ' + str(target_dir) + '/' + str(Path(qa_filepath.name).with_suffix('.tif')))

    return target_dir


def sentinel_harmonize_sr(s2_entry, target_dir, apply_bandpass=True):
    """Prepare Sentinel-2 NBAR from LaSRC.

    Args:
        scene_id (str): Scene identifier
        safel1c (str): path to SAFEL1C directory.
        sr_dir (str|Path): path to directory containing surface reflectance.
        target_dir (str): path to output result images.
        apply_bandpass - Apply the band pass processing. Default is True.

    Returns:
        str: path to folder containing result images.
    """
    # Generating Angle bands
    sz_path, sa_path, vz_path, va_path = s2angs.gen_s2_ang(str(s2_entry))

    target_dir.mkdir(parents=True, exist_ok=True)

    logging.info('Harmonization ...')
    # Sentinel-2 data set
    satsen = s2_entry.name[0:3]
    logging.info(f'SatSen: {satsen}')
    scene_id = Path(s2_entry).stem

    bands = ['sr_band2', 'sr_band3', 'sr_band4', 'sr_band8', 'sr_band8a', 'sr_band11', 'sr_band12']

    process_NBAR(s2_entry, scene_id, bands, sz_path, sa_path, vz_path, va_path, satsen, target_dir, apply_bandpass)

    return target_dir


def sentinel_harmonize(sentinel2_entry, target_dir, apply_bandpass=True):
    """Check if input surface reflectance is from Sen2cor or LaSRC and direct NBAR processing.

    Args:
        safel1c (str): path to SAFEL1C directory.
        scene_id (str): Scene identifier
        reflectance_data (str): path to directory containing surface reflectance.
        target_dir (str): path to output result images.
    """
    sentinel2_entry = Path(sentinel2_entry)
    target_dir = Path(target_dir)

    if sentinel2_entry.name.endswith('.SAFE'):  # Check if was processed with Sen2cor
        sentinel_harmonize_SAFE(sentinel2_entry, target_dir, apply_bandpass)
    else:
        sentinel_harmonize_sr(sentinel2_entry, target_dir, apply_bandpass)

    return
