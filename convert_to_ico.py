from PIL import Image

# Make sure this matches your PNG filename exactly:
img = Image.open("Stamppy Logo - Stamp Icon - Color.png")

# Save a multi-size ICO:
img.save("Stamppy.ico", format="ICO",
         sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
print("✅ Stamppy.ico generated successfully.")
