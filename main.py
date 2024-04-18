# Description: This is the main file for the 24BrainMRI_Preprocessing package. It is used to run the entire pipeline.
import os
import argparse
import logging
from pathlib import Path

# local imports
from src.extract_all import process_images
from src.segment_qc import segmentations_qc
from src.volume_check import calculate_volumes

if __name__ == "__main__":
    # parse args
    parser = argparse.ArgumentParser(description='Process images')
    parser.add_argument('--nifti', type=str, help='path to text file containing paths to the original nifti files')
    parser.add_argument('--mask', type=str, help='path text file containing paths to the segmentation masks')
    parser.add_argument('--output', type=str, help='path to contain the extracted files')
    parser.add_argument('--sid', type=str, help='path to the txt file containing the SIDs', default=None)
    parser.add_argument('--va', type=bool, help='if true, perform volumetric analysis on the segmented files', default=False)
    args = parser.parse_args()

    conformed_path_txt = Path(args.nifti)
    segmented_path_txt = Path(args.mask)
    output_path = Path(args.output)
    sid_file = Path(args.sid)
    perform_vol = args.va
    num_inputs = sum(1 for _ in open(conformed_path_txt))

    # create output directories
    output_path.mkdir(parents=True, exist_ok=True)
    txt_path = output_path / 'text_files'
    ext_path = output_path / 'extractions'
    txt_path.mkdir(parents=True, exist_ok=True)
    ext_path.mkdir(parents=True, exist_ok=True)

    if sid_file is None:
        sid_file = txt_path / 'sids.txt'
        with open(sid_file, 'w') as f:
            for i in range(num_inputs):
                f.write(f'{i}\n')

    # Extract the segmented files using Seg2Seg : check the README for further details
    logging.info('Running extraction of the segmented files using Seg2Seg...')
    process_images(conformed_path_txt, segmented_path_txt, txt_path, ext_path, num_of_files = num_inputs)
    
    # Run quality check on the segmented files
    logging.info('Running quality check on the segmented files...')
    qc_path = segmentations_qc(txt_path)
    logging.info(f'Quality check file saved to {qc_path}')

    # Perform volumetric analysis on the segmented files
    if perform_vol:
        logging.info('Running volumetric analysis on the segmented files...')
        calculate_volumes(conformed_path_txt, segmented_path_txt, sid_file, txt_path)
        logging.info(f'Volumetric analysis file saved to {txt_path / "volumetic_analysis.csv"}')
    else:
        logging.info('Skipping volumetric analysis on the segmented files...')

    logging.info("24BrainMRI_Preprocessing has finished running!")