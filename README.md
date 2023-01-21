# HeimdallSPAM

Simple spam filtering based on RandomForestClassifier

Usage: run_spam.bat
Uncomment the training part inside testing function

Program receives a path to a folder, and proceeds to classify all files in that folder like this:
```
File1Clean|cln
File2Spam|inf
```

This work was graded :
| Pos | Project | Version | Det | FP | Sc.1 | Time | Score |
|  --- |  --- |  --- |  --- |  --- |  --- |  --- |  --- |
| 3 | Heimdall SPAM | 3.0 | 99.59 | 0.98 | 97.64 | 0 | 97.64 |

Score is Det - 2*FP - Time

Training data not provided.
