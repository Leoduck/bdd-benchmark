# Runnign the script
To run the script for making graphs supply arguments for buddy and adiars data folders e.g.
```
python3 graphs.py data/buddy data/adiar
```
Then the script should create 3 png files :
1. "scatter_normal" : regular scatter plot of buddy vs adiar times on picotrav
2. "scatter_slowdown" : scatter plot of factor slowdown between adiar and buddy (x-axis is size of bdd after reorder)
3. "special" : 3-by-3 for the special cases

# TODO
 - make graphs for scalable examples quad, diamond, memo for buddy vs nested sweeping
    - should be either time on y-axis and N on x axis and then 2 lines one for buddy one for adiar
    - or we can have factor slowdown on y axis 