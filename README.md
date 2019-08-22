# Folder

Folder can be run with python 3 like so:```python3 folder.py path/to/data new/empty/destination/path 5```
This will create 5 folds in the second path.


You can also run it with an additional parameter, the percentage of the training set. This should be given as a number between 0 and 1. By default this is set to 0.8 (80%).
The python call will then look like this:  ```python3 folder.py path/to/data new/empty/destination/path 5 0.9```

To create a unique test set, you can use `uniqueFolder.py`. Usage is the same as folder.py.