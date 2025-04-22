import easyocr
reader = easyocr.Reader(['en'], gpu=False)  # Use 'gpu=True' if you have GPU support

result = reader.readtext(r'C:\Users\akh\Downloads\shared_folder\nobat\media\captcha\2.png')
for detection in result:
    text = detection[1]  # The detected text
    print(text)