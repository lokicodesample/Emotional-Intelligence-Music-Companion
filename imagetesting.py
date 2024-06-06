import cv2
import numpy as np
from keras.models import load_model

emotion_label = {0: "angry", 1: "happy", 2: "neutral", 3: "sad"}

# Load the saved model
loaded_model = load_model('Models/model_detect_emotional.h5')

# Load and preprocess your custom images
custom_image_path = 'Images/happy/happy1.jpg'

# Load the image in RGB format
custom_image = cv2.imread(custom_image_path)
custom_image = cv2.cvtColor(custom_image, cv2.COLOR_BGR2RGB)

# Convert to grayscale
custom_image_gray = cv2.cvtColor(custom_image, cv2.COLOR_RGB2GRAY)

# Resize the image to meet the input size requirement
custom_image_gray = cv2.resize(custom_image_gray, (71, 71))

# Normalize pixel values
custom_image_gray = custom_image_gray.astype('float32') / 255

# Expand dimensions to match the input shape expected by the model
custom_image_gray = np.expand_dims(custom_image_gray, axis=0)
custom_image_gray = np.expand_dims(custom_image_gray, axis=-1)

# Perform inference
predictions = loaded_model.predict(custom_image_gray)

# Interpret the predictions
predicted_class = np.argmax(predictions)

# Print the predicted class
print("Predicted Emotional:", emotion_label[predicted_class])

# Load the image
image = cv2.imread('Images/happy/happy1.jpg')

# Resize the image to fit within the screen size
# You can adjust the dimensions according to your screen resolution
screen_width, screen_height = 720, 720  # Example screen resolution
image = cv2.resize(image, (screen_width, screen_height))

# Put the emotion label at the top of the image
cv2.putText(image, "Predicted Emotion: " + emotion_label[predicted_class], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

# Display the resized image
cv2.imshow('Resized Image', image)

# Wait for a key press and then close the window
cv2.waitKey(0)
cv2.destroyAllWindows()






