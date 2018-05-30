
Main.py

For help use '  python main.py -h   '

To use this program, run it in the command line as python main.py with the following arguments

main.py -h 
  -To get help using the program

main.py {-tr, --train} -f path/to/DATA/aclImdb/
  - Train the classifier, given a pathname to the top directory containing the train-folder
  - Makes a text-file, that stores the state of the training algorithm and is used for classification

main.py {-cl , --classify} -f .
  - Use to classify one review, given a pathname to the review. If no proper path is found, e.g. by using .,
    the application will ask you to type a review in the terminal.
  - the training must already have been done, e.g. you need an nbc.txt file
 

main.py {-te, --test} -f path/to/DATA/aclImdb/
  -classify all the reviews in test directory in the DATA folder, give pathname to the DATA-folder
  - the training must already have been done, e.g. you need an nbc.txt file
