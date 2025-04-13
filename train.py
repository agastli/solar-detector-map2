from ultralytics import YOLO
import argparse

def train_model(
    model_path="yolov8n.pt",
    data_path="data/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16,
    project="runs/train",
    name="solar-panels"
):
    """
    Train a YOLOv8 model using the given configuration.
    """
    model = YOLO(model_path)  # Can be a pretrained or custom model

    model.train(
        data=data_path,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project=project,
        name=name,
        workers=4,
        device="cpu",  # Change to 'cuda' if you have a GPU
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv8 on solar panel dataset")

    parser.add_argument("--model", type=str, default="yolov8n.pt", help="YOLO model to start from")
    parser.add_argument("--data", type=str, default="data/data.yaml", help="Path to dataset YAML")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size for training")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--project", type=str, default="runs/train", help="Project directory")
    parser.add_argument("--name", type=str, default="solar-panels", help="Run name")

    args = parser.parse_args()

    train_model(
        model_path=args.model,
        data_path=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=args.project,
        name=args.name
    )
