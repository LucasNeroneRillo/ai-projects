The hardest part of the project was probably configuring the environment.
After I managed to do it through Anaconda, I quickly managed to load the data.
Then, I begun to work on the neural network, starting with one similar to that from the lecture.

After some testings on number of layers, types of activation functions, and number of nodes,
I got to a reasonably good network, that took around 10 minutes to train and had a 92% accuracy.

I then tried different actions on that neural network and kept track of which were useful.
I discovered that batch normalization was essential for good accuracy,
and that dropout was the most sensitive part of the network:
without it, the model overfits, and by dropping to many nodes, you lose accuracy.

After several training processes with slightly different networks,
I took the changes that worked and built a different network.
I repeated the process of changing minor things, now to reduce time.
One thing worked amazingly: I had two convolutional layers with two max pooling layers in between,
and by adding the two max pooling layers together, between the first and second convolutional ones,
(instead of two 2x2 poolings, I did one of 5x5) I reduced the training time by half.