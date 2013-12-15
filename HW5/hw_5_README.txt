Partner 1: Thomas Lo

EID: TL7543


Partner 2: Zachary Tschirhart

EID: ZST75


Homework #5



For our classifier, we used a training sample size of 49 snapshots. We had 11 pictures of the cube, 13 pictures of Steve, 14 pictures of Sydney, and 11 pictures of the tree. We used a validation sample size of 5 snapshots of each object, for a total of 20 images. Our testing sample was the same size as the validation sample.



We decided to use relatively basic features in order to classify the objects. We defined an edge pixel as any pixel with a brightness value of over 100. First we needed to obtain some basic data for each image. We found the percentage of pixels that were edge pixels. Then we used the percentage of pixels in the top half of the picture that were horizontally oriented and vertically oriented. We did the same for the bottom half of the picture. The last value we collected was the percentage of pixels in the top third of the image that were edge pixels. This last feature specifically targeted the identification of the tree, while the other features were more general.

In our training method, we took each image in the training set and calculated the six features for each picture.

We put this data into a spreadsheet and fiddled around with the data until we figured out what cut-off values offered good results with the validation set. In the end, we came up with six features to use in classifying object.

	1. percentage of edge pixels > 1.75%

	2. percentage of pixels oriented horizontally in the top half < 67.7%

	3. percentage of pixels oriented vertically in the top half > 10.5%

	4. percentage of pixels oriented horizontally in the bottom half < 41%
	5. percentage of pixels oriented vertically in the bottom half < 18.8%

	6. percentage of edge pixels in the top third > 0.73%



Using these cut-off values, we achieved 75% identification accuracy for the validation images. Cubes and trees were identified with 100% accuracy, but the classifier had trouble consistently identifying Steve and Sydney. The main cause of this inaccuracy was probably because the values of the features of the Steve and Sydney images were very close as well as extra edges picked up from the background. This could have been fixed by using more narrow features that differentiates Sydney and Steve. Below is a list of the validation images and what they were identified as.

	1. cube1 - identified as cube

	2. cube2 - identified as cube

	3. cube3 - identified as cube

	4. cube4 - identified as cube

	5. cube5 - identified as cube

	6. steve1 - identified as Steve

	7. steve2 - identified as Steve

	8. steve3 - identified as Steve

	9. steve4 - identified as Sydney

	10. steve5 - identified as tree

	11. sydney1 - identified as Cube

	12. sydney2 - identified as Sydney

	13. sydney3 - identified as Sydney

	14. sydney4 - identified as Cube

	15. sydney5 - identified as Steve

	16. tree1 - identified as tree

	17. tree2 - identified as tree

	18. tree3 - identified as tree
 
	19. tree4 - identified as tree

	20. tree5 - identified as tree



For the testing set of images, we had an accuracy of 60%. Cubes and trees were still identified with relative consistency, while Steve and Sydney still had troubles being identified. Again, these inconsistencies may have been caused by background edges being picked up and also due to variable distance of each different object. Below is a list of the testing images and what they were identified as.

	1. cube1 - identified as cube

	2. cube2 - identified as cube

	3. cube3 - identified as cube

	4. cube4 - identified as cube

	5. cube5 - identified as sydney

	6. steve1 - identified as Steve

	7. steve2 - identified as Sydney

	8. steve3 - identified as Steve

	9. steve4 - identified as Steve

	10. steve5 - identified as Steve

	11. sydney1 - identified as Tree

	12. sydney2 - identified as Cube

	13. sydney3 - identified as Cube

	14. sydney4 - identified as Sydney
	15. sydney5 - identified as Cube

	16. tree1 - identified as Sydney

	17. tree2 - identified as tree

	18. tree3 - identified as tree
 
	19. tree4 - identified as tree

	20. tree5 - identified as Steve
