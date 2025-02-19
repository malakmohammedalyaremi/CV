from ultralytics import YOLO

model = YOLO ("yolo11s.pt")

results = model.predict(source=r"C:\Users\USER\OneDrive\Pictures\car.jpg")
        
results [0].show() 
                        
                        