import cv2

# Initialize global variables for cropping
cropping = False
start_point = (0, 0)
end_point = (0, 0)
cropped_image = None

# Mouse callback function to handle the drawing
def mouse_crop(event, x, y, flags, param):
    global start_point, end_point, cropping, cropped_image
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Start drawing the rectangle
        start_point = (x, y)
        cropping = True

    elif event == cv2.EVENT_MOUSEMOVE:
        if cropping:
            # Update the endpoint as the mouse moves
            end_point = (x, y)
    
    elif event == cv2.EVENT_LBUTTONUP:
        # Stop drawing the rectangle and finalize the crop
        end_point = (x, y)
        cropping = False
        
        # Crop the region of interest
        x1, y1 = start_point
        x2, y2 = end_point
        cropped_image = image[y1:y2, x1:x2]  # Crop using the coordinates
        
        # Display the cropped region
        cv2.imshow("Cropped Image", cropped_image)

# Load the image
image = cv2.imread("download (1).png")  # Replace with your image path
clone = image.copy()

cv2.namedWindow("Image")
cv2.setMouseCallback("Image", mouse_crop)

while True:
    temp_image = clone.copy()
    if cropping:
        # Draw the rectangle on the copy of the image
        cv2.rectangle(temp_image, start_point, end_point, (0, 255, 0), 2)

    # Display the image
    cv2.imshow("Image", temp_image)
    
    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
