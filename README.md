This project aims to be able to show in a CVS file a resume of a receipt.
Furthermore uses:
  - EasyOCR for image-to-text recognition
  - Pandas for data frame manipulation
  - Pillow and Pillow_heif for Image manipulation and conversion if the Image type is Heic (since OCR can not handle .heic files)

The program will ask every boot if you want to create a new receipt or update one already existing;
automatically will extract text and perform string manipulation to have a final list of [(Product, Price),(...),...]
which will be used to create a dataframe or append to an already existing one
Photo are pre-processed with iphone's photo editor to improve contrast and drop saturation

To execute this program use:
- python Scontrini.py followed by:
- N to create a new receipt / U to update an existing one;
- Path for the image
Example: python Scontrini.py N path\to\your\image

Use as working directory: Receipts_scanner-main
test images are located in a folder named 'input_img' accessible through relative path: input_img\nameoftheimg
outuput will be stored in the 'output' folder
  


