
Main.py

For help use '  python main.py -h   '

To use this program, run it in the command line as python main.py with the following arguments, traing must be done first.
Traing will create a new file called nbc.txt, which will be used to classify. 

main.py -h 
  -To get help using the program

main.py {-tr, --train} -f path/to/DATA/aclImdb/trainingSet/
  - Train the classifier, given a pathname to the top directory containing the train-folder
  - Makes a text-file, that is used for classification 

main.py {-cl , --classify} -f .
  -Use to classify one review, given a pathname to the review
  - the training must already have been done
 

main.py {-te, --test} -f path/to/DATA/aclImdb/testSet/
  -classify all the reviews in test directory in the DATA folder, give pathname to the DATA-folder


example usage:

python main.py -tr -f DATA/aclImdb/train/

python main.py -te -f DATA/aclImdb/test/

python main.py -cl -f . < DATA/aclImdb/test/next/0_2.txt
    - This pipes a review to the program
