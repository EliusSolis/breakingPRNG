# breakingPRNG
A proof of concept attack agains a lfsr based prng


### Structure

Class `Rand` is a recreation of the PRNG in python.
Class `Randcrack` recreates the interan state of `Rand` after being given 16 outputs of 2 bytes

Function `main` creates a new `Rand` instance with random seeds and check if the predicted value of `Randcrack` is correct, the process is repeated 10000 times.
