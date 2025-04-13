from ultralytics import YOLO
from PIL import Image
import numpy as np
import pandas as pd
import streamlit as st

from src.utils.logger import logger


def detect_panels(image_path, model_path):
    """
    Detect solar panels in the input image using YOLOv8.

    Parameters:
    - image_path: Path to the input image.
    - model_path: Path to the YOLOv8 model file.

    Returns:
    - Annotated image with bounding boxes (PIL.Image)
    - Pandas DataFrame of detections
    """
    # Load the specified YOLOv8 model
    model = YOLO(model_path)
    try:
        logger.info(f"Running detection on image: {image_path}")
        results = model(image_path)
        logger.debug(f"Raw detection output: {results[0].to_df().head()}")
        # Render image with annotations
        img_array = results[0].plot()
        annotated_img = Image.fromarray(img_array)

        # Convert to dataframe
        detection_df = results[0].to_df()

        if detection_df.empty:
            st.warning("No detections found in the image.")
            return annotated_img, pd.DataFrame()

        if "box" not in detection_df.columns:
            st.error("Detection output is missing 'box' field. Please check model output.")
            return annotated_img, pd.DataFrame()

        # Unpack box coordinates
        try:
            detection_df["xmin"] = detection_df["box"].apply(lambda b: b["x1"])
            detection_df["xmax"] = detection_df["box"].apply(lambda b: b["x2"])
            detection_df["ymin"] = detection_df["box"].apply(lambda b: b["y1"])
            detection_df["ymax"] = detection_df["box"].apply(lambda b: b["y2"])
            detection_df.drop(columns=["box"], inplace=True)
        except Exception as e:
            st.error(f"Error unpacking bounding boxes: {e}")
            return annotated_img, pd.DataFrame()

        st.write("🔍 Detection DataFrame Preview:", detection_df.head())

        return annotated_img, detection_df

    except Exception as ex:
        st.error(f"Detection failed: {ex}")
        return Image.open(image_path), pd.DataFrame()
