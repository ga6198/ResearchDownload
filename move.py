import os
import math
import zipfile

#function to split projects between training, testing, and validation sets
def split_data(fileList):
    #establish 80/20 split between training files and rest
    firstCutoff = (len(fileList)/10) * 8
    firstCutoff = math.ceil(firstCutoff)
    print(firstCutoff)
    trainingSet = fileList[:firstCutoff]
    remainingFileList = fileList[firstCutoff:]

    #Split remaining 20% of files in half to give test/validation sets
    half = len(remainingFileList)//2
    testSet = remainingFileList[:half]
    validationSet = remainingFileList[half:]

    return trainingSet, testSet, validationSet

def unzip_and_move(file_list, target_dir):
    for file in file_list:
        #unzip a file to the target directory
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(target_dir)

        #delete the zip file
        try:
            os.remove(file)
        except:
            print("Error: could not remove file", file)
    

#get all files
files = [f for f in os.listdir('.') if os.path.isfile(f)]

#filter for the downloaded zip files
zip_files = [f for f in files if f.endswith('.zip')]

for f in zip_files:
    print(f)

training_files, test_files, validation_files = split_data(zip_files)

print("Training files:", training_files)
print("Test files:", test_files)
print("Validation files:", validation_files)

print("Unzipping and moving files...")
unzip_and_move(training_files, "../research_download/train")
unzip_and_move(test_files, "../research_download/test")
unzip_and_move(validation_files, "../research_download/val")

