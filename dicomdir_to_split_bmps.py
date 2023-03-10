import os
import sys
import shutil
from os.path import join
import imageio
import pydicom
from numpy import uint8

DICOMDIR_PATH = sys.argv[5]
DESIRED_SERIES = sys.argv[6]


def dicom_to_bmp():
    for root, _, files in os.walk(DICOMDIR_PATH):
        for file in files:
            if file == "dicomdir":
                dataset = pydicom.dcmread(join(root, file))
                break

    for patient_record in dataset.patient_records:
        studies = patient_record.children
        for study in studies:
            all_series = study.children
            for series in all_series:
                if series.SeriesDescription == DESIRED_SERIES:
                    image_records = series.children
                    break

    image_filenames = [join(DICOMDIR_PATH, *image_rec.ReferencedFileID)
                       for image_rec in image_records]
    images = [pydicom.dcmread(image_filename)
              for image_filename in image_filenames]

    try:
        os.mkdir("Grid BMPs")
    except FileExistsError:
        shutil.rmtree("Grid BMPs")
        os.mkdir("Grid BMPs")

    for frame_num, image in enumerate(images, 1):
        imageio.imwrite(join("Grid BMPs", f"Frame {str(frame_num).zfill(3)}.bmp"),
                        uint8(image.pixel_array))


def grid_images_to_folders():
    height_in_pixels = int(sys.argv[1])
    width_in_pixels = int(sys.argv[2])
    image_rows = int(sys.argv[3])
    image_cols = int(sys.argv[4])

    istep = height_in_pixels//image_rows
    jstep = width_in_pixels//image_cols

    try:
        os.mkdir("Split BMPs")
    except FileExistsError:
        shutil.rmtree("Split BMPs")
        os.mkdir("Split BMPs")
    frame_number = 0
    for root, _, files in os.walk("Grid BMPs"):
        for file in files:
            if file.endswith(".bmp"):
                frame_number += 1
                sub_im = imageio.imread(join(root, file))

                os.mkdir(f"Split BMPs/Frame {str(frame_number).zfill(3)}")
                slice_number = 1
                for i in range(0, height_in_pixels, istep):
                    for j in range(0, width_in_pixels, jstep):
                        imageio.imwrite(join(os.getcwd(), "Split BMPs",
                                             f"Frame {str(frame_number).zfill(3)}",
                                             f"Slice {str(slice_number).zfill(3)}.bmp"),
                                        sub_im[i:i+istep, j:j+jstep])
                        slice_number += 1
    shutil.rmtree("Grid BMPs")


def main():
    dicom_to_bmp()
    grid_images_to_folders()


if __name__ == "__main__":
    main()
