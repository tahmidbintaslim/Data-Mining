import os
import re
from nltk.corpus import stopwords
from nltk.stem.porter import *
import collections
import numpy
import time
import cPickle as pickle

#
# Pre-Process Part
#

startTime = time.time()
print "Starting...\n"

# Identify Category
categoryList =  os.listdir("./dataset/Reuters21578-Apte-115Cat/training/")
categoryTestList = os.listdir("./dataset/Reuters21578-Apte-115Cat/test/")

# StopWord Definition
stopwordsList = stopwords.words('english')
stemmer = PorterStemmer()
fileNum = 0
fileTestNum = 0
categoryNum = 0
categoryTestNum = 0
outputFile = open('pre_processed_data_object_naivebayes', 'wb')

# File Fraction size to Read. Set between 0.1 and 1
fileFractionSize = 1
fileTestFractionSize = 1

# Define Regular Expression to pre-process strings. Only AlphaNumeric and whitespace will be kept.
strPattern = re.compile('[^a-zA-Z0-9 ]')

# A dictionary which keeps token and its frequency for each category. It will keep a Dictionary in a Dictionary.
# key - category, value-{'term':frequency}
# Example : {'acq' : {'hi':1,'compu':3,'move':1 ...}}
categoryAlphaNumericStrStemmedDict = {}
categoryTestAlphaNumericStrStemmedDict = {}

# A dictionary which keeps token, its frequency, and category for each file. It is layered Dictionary structure.
# 1st layer Dict {A}: key - category, value-{'term':frequency}
# 2nd layer Dict {B}: key - filename, value-{A}
# Example : {'000056' : {'acq' : {'hi':1, 'compu:3, 'move':1 ...}}}
fileAlphaNumericStrStemmedDict = {}
fileTestAlphaNumericStrStemmedDict = {}

# A list which keeps whole vocabularies throughout whole categories. It will be sorted.
# Example : ['current', 'curtail', 'custom', 'cut', 'cuurent', 'cvg', 'cwt', 'cypru', 'cyrpu', 'd', 'daili' ...]
wholeVocabularySet = set()
wholeVocabularyList = []
wholeTestVocabularySet = set()
wholeTestVocabularyList = []

wholeVocabularyFrequency = 0
wholeTestVocabularyFrequency = 0

# A dictionary which keeps entire vocabulary and its frequency across whole categories
# Example : {'current' : 110, 'said' : 10000 ...... }
wholeVocabularyFrequencyDict = {}
wholeVocabularyTestFrequencyDict = {}

# A dictionary which keeps number of files in each category
# Example : {'acq': 115, 'alum': 222 ...}
numberOfFilesInEachCategoryDict = {} 
numberOfFilesInEachCategoryTestDict = {} 

# A dictionary which keeps fraction of [number of files in each category] / [number of entire files]
# Example : {'acq':0.015, 'alum':0.031 ...}
fractionOfFilesInEachCategoryDict = {} 
fractionOfFilesInEachCategoryTestDict = {} 


# [Naive Bayes YEN] dictionary to contain assign category from test set {'acq' :['0012', '0033', '2525'], ...}
assignedCategoryTest = {}
assignedCategory = {}
fileAssignedCategory = {}
fileAssignedCategoryTest = {}
# to keep frequency of each word in file without information about the category {'0001' :{'hi':1, 'compu:3, 'move':1 ...}, '088' : {'hi':3, 'compu:23, 'move':31 ...}}
wordFrequencyInFileTest = {}
wordFrequencyInFile = {}


# Read Training Data Set
print "\nReading Training data Set"
print "Elap(s)\Dur(s)\tCategory#\tName\t#ofFile\t#ofUniqueTerms\t#Frequency"

#Iterate each category and create vector space for each category

for category in categoryList:

    tmpTime = time.time()

    # Temporary code to reduce time to process. Eliminate when processing entire set
    
#     if category == 'acq' or category == '.DS_Store':
#         continue
#     if categoryNum == 10:
#         break
     
    fileInCategoryList = os.listdir("./dataset/Reuters21578-Apte-115Cat/training/" + category + "/")
    tmpCategoryAlphaNumericStrStemmedDict = {}
    # categoryAlphaNumericStrStemmedDict[categoryNum][0] = category
    # categoryTmpColumn = {}
    # categoryTmpColumn.append(str(category))
    tmpFileNum = 0
    tmpFreqPerCategory= 0
    tmpNumberOfUniqueTermPerCategory = 0
    tmpNumberOfTermPerCategory = 0
    
    #[Naive Bayes - YEN] create dictionary of each category {'acq' : ['01213', '31333', '00001'], .....}
    assignedCategory[category] = fileInCategoryList
    
    for fileToTrain in fileInCategoryList:
        fileToTrainPath = './dataset/Reuters21578-Apte-115Cat/training/' + category + '/' + fileToTrain
        
        #[Naive Bayes - YEN] create dictionary of each file {'00313' :'acq' , .....}
        if fileToTrain in fileAssignedCategory.keys():
            fileAssignedCategory[fileToTrain].append(category)            
        else:               
            fileAssignedCategory[fileToTrain] = [category]    
        
           
            
        # Check the file size and read some fraction of the file defined in "fileFractionSize" variable
        filesize = os.path.getsize(fileToTrainPath)
        chunkReadSize = int(round(filesize * fileFractionSize))
        f = open(fileToTrainPath)
        fileStr = f.read(chunkReadSize)
        fileTmpColumn = {}
        fileTmpColumn1 = {}
        # fileTmpColumn.append(str(category))
        # fileTmpColumn.append(str(fileToTrain))

        # Remove non alphanumeric characters in the chunk
        fileAlphaNumericStr = re.sub(strPattern, ' ', fileStr)

        # Convert to lower case
        fileAlphaNumericStr = fileAlphaNumericStr.lower()

        # Remove Stop Words and Tokenize the chunk into a List by using whitespace
        fileAlphaNumericStrNoStopWords = ' '.join([word for word in fileAlphaNumericStr.split() if word not in stopwordsList])
        fileAlphaNumericStrList = fileAlphaNumericStrNoStopWords.split()
#         fileAlphaNumericStrList = fileAlphaNumericStr.split()

        # Apply Porter Stemmer and Put token and frequency to One Dict
        tmpFileAlphaNumericStrStemmedDict = {}

        # Create vector space (Dict) for each category
        for words in fileAlphaNumericStrList:
            tmp = stemmer.stem(words)
            tmp1 = tmpFileAlphaNumericStrStemmedDict.get(tmp)
            tmp2 = tmpCategoryAlphaNumericStrStemmedDict.get(tmp)
            if tmp1 == None:
                tmpFileAlphaNumericStrStemmedDict[tmp] = 1
            else:
                tmpFileAlphaNumericStrStemmedDict[tmp] = tmp1 + 1
            if tmp2 == None:
                tmpCategoryAlphaNumericStrStemmedDict[tmp] = 1
            else:
                tmpCategoryAlphaNumericStrStemmedDict[tmp] = tmp2 + 1
            tmpFreqPerCategory += 1    
            if tmp not in wholeVocabularySet:
                wholeVocabularySet.add(tmp)

        fileTmpColumn1[category] = tmpFileAlphaNumericStrStemmedDict
        # fileTmpColumn.append(tmpFileAlphaNumericStrStemmedDict)
        # fileTmpColumn[str(fileToTrain)] = fileTmpColumn1 
        
      
            
            
        fileAlphaNumericStrStemmedDict[fileToTrain] = fileTmpColumn1
        fileNum += 1
        tmpFileNum += 1
        
    # categoryTmpColumn.append(tmpCategoryAlphaNumericStrStemmedDict)
    categoryAlphaNumericStrStemmedDict[category] = tmpCategoryAlphaNumericStrStemmedDict
    categoryNum += 1
    wholeVocabularyFrequency += tmpFreqPerCategory
    numberOfFilesInEachCategoryDict[category] = tmpFileNum
    
#     print "%6.3g"%(time.time() - startTime) + "\t" + "%6.3g"%(time.time() - tmpTime) + "\t" + str(categoryNum) +  "\t" + category + "\t" + str(tmpFileNum) + "\t" + str(len(tmpCategoryAlphaNumericStrStemmedDict)) + "\t" + str(tmpFreqPerCategory)




# print "\nReading Test data Set"
# print "Elap(s)\Dur(s)\tCategory#\tName\t#ofFile\t#ofUniqueTerms\t#Frequency"

#Iterate each TEST category and create vector space for each category
duplicatedTest = 0
for categoryTest in categoryTestList:

    tmpTime = time.time()

    # Temporary code to reduce time to process. Eliminate when processing entire set
#     if categoryTest == 'acq' or categoryTest == '.DS_Store':
#         continue
#     if categoryTestNum == 10:
#         break
    
    fileInCategoryTestList = os.listdir("./dataset/Reuters21578-Apte-115Cat/test/" + categoryTest + "/")
    
    #[Naive Bayes - YEN] create dictionary of each category {'acq' : ['01213', '31333', '00001'], .....}, can be used in other way of evaluation
    assignedCategoryTest[categoryTest] = fileInCategoryTestList
    
    
    tmpCategoryTestAlphaNumericStrStemmedDict = {}
    # categoryAlphaNumericStrStemmedDict[categoryNum][0] = category
    # categoryTestTmpColumn = []
    # categoryTestTmpColumn.append(str(categoryTest))
    tmpFileTestNum = 0
    tmpFreqPerCategoryTest= 0
    tmpNumberOfUniqueTermPerCategoryTest = 0
    tmpNumberOfTermPerCategoryTest = 0
    
    for fileToTest in fileInCategoryTestList:
        fileToTestPath = './dataset/Reuters21578-Apte-115Cat/test/' + categoryTest + '/' + fileToTest
       
        #[Naive Bayes - YEN] create dictionary of each category {'0012' : 'acq', ...}
        if fileToTest in fileAssignedCategoryTest.keys():                
            fileAssignedCategoryTest[fileToTest].append(categoryTest)
        else:          
            fileAssignedCategoryTest[fileToTest] = [categoryTest]
           
         
        
        
        # Check the file size and read some fraction of the file defined in "fileFractionSize" variable
        filesizeTest = os.path.getsize(fileToTestPath)
        chunkTestReadSize = int(round(filesizeTest * fileTestFractionSize))
        f = open(fileToTestPath)
        fileTestStr = f.read(chunkTestReadSize)
        fileTestTmpColumn = {}
        # fileTestTmp1Column = {}
        
        # fileTestTmpColumn.append(str(categoryTest))
        # fileTestTmpColumn.append(str(fileToTest))

        # Remove non alphanumeric characters in the chunk
        fileTestAlphaNumericStr = re.sub(strPattern, ' ', fileTestStr)

        # Convert to lower case
        fileTestAlphaNumericStr = fileTestAlphaNumericStr.lower()

        # Remove Stop Words and Tokenize the chunk into a List by using whitespace
        fileTestAlphaNumericStrNoStopWords = ' '.join([word for word in fileTestAlphaNumericStr.split() if word not in stopwordsList])
        fileTestAlphaNumericStrList = fileTestAlphaNumericStrNoStopWords.split()

        # Apply Porter Stemmer and Put token and frequency to One Dict
        tmpFileTestAlphaNumericStrStemmedDict = {}

        # Create vector space (Dict) for each category
        for words in fileTestAlphaNumericStrList:
            tmp = stemmer.stem(words)
            if tmpFileTestAlphaNumericStrStemmedDict.get(tmp) == None:
                tmpFileTestAlphaNumericStrStemmedDict[tmp] = 1
            else:
                tmpFileTestAlphaNumericStrStemmedDict[tmp] += 1
            if tmpCategoryTestAlphaNumericStrStemmedDict.get(tmp) == None:
                tmpCategoryTestAlphaNumericStrStemmedDict[tmp] = 1
            else:
                tmpCategoryTestAlphaNumericStrStemmedDict[tmp] += 1
            tmpFreqPerCategoryTest += 1    
            if tmp not in wholeTestVocabularySet:
                wholeTestVocabularySet.add(tmp)
        # [ YEN ]        
        if fileToTest in fileTestAlphaNumericStrStemmedDict.keys():
            duplicatedTest = duplicatedTest + 1
            
        fileTestTmpColumn[categoryTest] = tmpFileTestAlphaNumericStrStemmedDict
        # fileTestTmpColumn.append(tmpFileTestAlphaNumericStrStemmedDict)
        fileTestAlphaNumericStrStemmedDict[fileToTest] = fileTestTmpColumn
        
        
        
        fileTestNum += 1
        tmpFileTestNum += 1
        
    # categoryTestTmpColumn.append(tmpCategoryTestAlphaNumericStrStemmedDict)
    categoryTestAlphaNumericStrStemmedDict[categoryTest] = tmpCategoryTestAlphaNumericStrStemmedDict
    categoryTestNum += 1
    wholeTestVocabularyFrequency += tmpFreqPerCategoryTest
    numberOfFilesInEachCategoryTestDict[categoryTest] = tmpFileTestNum
    
    print "%6.3g"%(time.time() - startTime) + "\t" + "%6.3g"%(time.time() - tmpTime) + "\t" + str(categoryTestNum) +  "\t" + categoryTest + "\t" + str(tmpFileTestNum) + "\t" + str(len(tmpCategoryTestAlphaNumericStrStemmedDict)) + "\t" + str(tmpFreqPerCategoryTest)


# Sort entire Vocabulary
wholeVocabularyList = list(wholeVocabularySet)
wholeVocabularyList.sort()

wholeTestVocabularyList = list(wholeTestVocabularySet)
wholeTestVocabularyList.sort()




# 
# print
# print "Statistics of Entire Training data Set"
# print "# of Categories:\t" + str(categoryNum)
# print "# of Files:\t" + str(fileNum)
# print "# of Vocabularies:\t" + str(len(wholeVocabularyList))
# print "# of Frequency:\t" + str(wholeVocabularyFrequency)


# print
# print wholeVocabularyList

# for i in range(0,categoryNum):
#    print str(categoryAlphaNumericStrStemmedDict[i][0]) + " ::::::: " + str(categoryAlphaNumericStrStemmedDict[i][1])


# A two dimensional List which keeps frequency of term per category. 
# row = category. column = frequency of each term in that category.
# For term list, we are using whole terms across entire categories.
# Example : category- acq, bop, term- 'commonplac', 'commonwealth', 'commun'
#           commonplac   commonwealth  commun
#    acq         7              2         0
#    bop         8              9         1 
termFrequencyPerCategoryList = []

# Creating A two dimensional List which keeps frequency of term per category
for key,value in categoryAlphaNumericStrStemmedDict.iteritems():
    tmpColumn = []
    tmpColumn.append(key)
    for term in wholeVocabularyList:
        tmp = value.get(term)
        if tmp == None:
            tmpColumn.append(0)
        else:
            tmpColumn.append(tmp)
    termFrequencyPerCategoryList.append(tmpColumn)

# Put frequency of each terms across entire categories
for key1, value1 in categoryAlphaNumericStrStemmedDict.iteritems():
    tmpDict = value1
    for key, value in tmpDict.iteritems():
        tmp = wholeVocabularyFrequencyDict.get(key)
        if tmp == None:
            wholeVocabularyFrequencyDict[key] = value
        else:
            wholeVocabularyFrequencyDict[key] = tmp + 1

# Put frequency of each terms across entire categories
for key1, value1 in categoryTestAlphaNumericStrStemmedDict.iteritems():
    tmpDict = value1
    for key, value in tmpDict.iteritems():
        tmp = wholeVocabularyTestFrequencyDict.get(key)
        if tmp == None:
            wholeVocabularyTestFrequencyDict[key] = value
        else:
            wholeVocabularyTestFrequencyDict[key] = tmp + 1

# for key1, value1 in fileAlphaNumericStrStemmedDict.iteritems():
#     for key,value in value1.iteritems():
#         print key + ":" + key1
        
# Calculate fractionOfFilesInEachCategoryDict
# for key1, value1 in fileAlphaNumericStrStemmedDict.iteritems():
#     for key, value in value1.iteritems():
#         tmp = numberOfFilesInEachCategoryDict.get(key)
#         if tmp == None:
#             numberOfFilesInEachCategoryDict[key] = 1
#         else:
#             numberOfFilesInEachCategoryDict[key] = tmp + 1


#[Naive Bayes - YEN] convert to float
for key1, value1 in numberOfFilesInEachCategoryDict.iteritems():
    fractionOfFilesInEachCategoryDict[key1] = float(value1) / fileNum

# Calculate fractionOfFilesInEachCategoryTestDict
# for key1, value1 in fileTestAlphaNumericStrStemmedDict.iteritems():
#     for key, value in value1.iteritems():
#         tmp = numberOfFilesInEachCategoryTestDict.get(key)
#         if tmp == None:
#             numberOfFilesInEachCategoryTestDict[key] = 1
#         else:
#             numberOfFilesInEachCategoryTestDict[key] = tmp + 1

#[Naive Bayes - YEN] convert to float
for key1, value1 in numberOfFilesInEachCategoryTestDict.iteritems():
    fractionOfFilesInEachCategoryTestDict[key1] = float(value1) / fileTestNum
    


# [Naive Bayes YEN] Dictionary wordFrequencyInFileTest
# to keep frequency of each word in file without information about the category {'0001' :{'hi':1, 'compu:3, 'move':1 ...}, '088' : {'hi':3, 'compu:23, 'move':31 ...}}
for fileTest in fileTestAlphaNumericStrStemmedDict.keys():
    categoryAndFrequency = fileTestAlphaNumericStrStemmedDict[fileTest]
    wordFrequencyInFileTest[fileTest] = categoryAndFrequency[categoryAndFrequency.keys()[0]]
    
for fileTrain in fileAlphaNumericStrStemmedDict.keys():
    categoryAndFrequency = fileAlphaNumericStrStemmedDict[fileTrain]
    wordFrequencyInFile[fileTrain] = categoryAndFrequency[categoryAndFrequency.keys()[0]]
    
    
           
pickle.dump(fileFractionSize, outputFile, -1)
pickle.dump(fileTestFractionSize, outputFile, -1)
pickle.dump(categoryAlphaNumericStrStemmedDict, outputFile, -1)
pickle.dump(categoryTestAlphaNumericStrStemmedDict, outputFile, -1)
pickle.dump(fileAlphaNumericStrStemmedDict, outputFile, -1)
pickle.dump(fileTestAlphaNumericStrStemmedDict, outputFile, -1)
pickle.dump(wholeVocabularyList, outputFile, -1)
pickle.dump(wholeTestVocabularyList, outputFile, -1)
pickle.dump(wholeVocabularyFrequency, outputFile, -1)
pickle.dump(wholeTestVocabularyFrequency, outputFile, -1)
pickle.dump(wholeVocabularyFrequencyDict, outputFile, -1)
pickle.dump(wholeVocabularyTestFrequencyDict, outputFile, -1)
pickle.dump(numberOfFilesInEachCategoryDict, outputFile, -1)
pickle.dump(numberOfFilesInEachCategoryTestDict, outputFile, -1)
pickle.dump(fractionOfFilesInEachCategoryDict, outputFile, -1)
pickle.dump(fractionOfFilesInEachCategoryTestDict, outputFile, -1)
pickle.dump(categoryNum, outputFile, -1)
pickle.dump(fileNum, outputFile, -1)
pickle.dump(categoryTestNum, outputFile, -1)
pickle.dump(fileTestNum, outputFile, -1)
pickle.dump(termFrequencyPerCategoryList, outputFile, -1)

#[Naive Bayes YEN]
pickle.dump(assignedCategory, outputFile, -1)
pickle.dump(assignedCategoryTest, outputFile, -1)
pickle.dump(fileAssignedCategory, outputFile, -1)
pickle.dump(fileAssignedCategoryTest, outputFile, -1)
pickle.dump(categoryList, outputFile, -1)
pickle.dump(categoryTestList, outputFile, -1)
pickle.dump(wordFrequencyInFile, outputFile, -1)
pickle.dump(wordFrequencyInFileTest, outputFile, -1)

print 

# Define TF-IDF based Cosine Similarity algorithm    
def tfidfCosineSimilarity(list):
    print "\nTF-IDF Cosine Similarity Algorithm\n"

# Define TF-IDF based Cosine Similarity algorithm in Detail    
def tfidfCosineSimilarityDetail(list):
    print "\nTF-IDF Cosine Similarity Algorithm\n"

# Define Decision Tree algorithm. 
def decisionTree(list):
    print "\nDecision Tree Algorithm\n"
    
# Define Decision Tree Algorithm in detail
def decisionTreeDetail(list):
    print "\nDecision Tree Algorithm\n"

# Define Naive Bayes algorithm
def naiveBayes(list):
    print "\nNaive Bayes Algorithm\n"

# Define Naive Bayes algorithm in detail
def naiveBayesDetail(list):
    print "\nNaive Bayes Algorithm\n"

# Execute TF-IDF based Cosine Similarity algorithm    
tfidfCosineSimilarity(termFrequencyPerCategoryList)

# Execute Decision Tree algorithm
decisionTree(termFrequencyPerCategoryList)

# Execute NaiveBayes algorithm
naiveBayes(termFrequencyPerCategoryList)



# [YEN]
# print "duplicated " + str(duplicated)    
# print "duplicated Test " + str(duplicatedTest)
# print "fileAssignedCategoryTest", fileAssignedCategoryTest
# print "fileAssignedCategory" , fileAssignedCategory
#print len(fileTestAlphaNumericStrStemmedDict)