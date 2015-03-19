# Cerulean

This project contains a neural network made by Matthew Levine some time in Winter 2015. The network is a simple mlp with some advanced hyperparameters like dropout.

This implementation is influenced a lot by the terrific matlab implementation by Rasmussen. Right now, this is pretty slow; I dream of moving large parts of it to C (specifically the costly parts). 
There is a reasonable amount of OO involved, though the primary network is structured as a library with OO interpserced where relevant (this is on purpose, for clarity).

There is a lso an entirely custom Python IDe as a subpackage which emulates Matalb's design environment and has some cool features like graphing project structure. I made
that for debugging... it was probable a pass-the-salt problem...

There is also a simple pltter included because I have a confusingly passionate hatred for matplotlib and its installation.

More details to come very shortly...
