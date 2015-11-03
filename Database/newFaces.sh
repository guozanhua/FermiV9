#!/bin/bash

cd faces_black

# convert -modulate 5,5,100 

cd basic_emotions
for a in *.png; do convert -modulate 5,5,100 "$a" "$a"; done
cd ..

cd blinking_animation
for a in *.png; do convert -modulate 5,5,100 "$a" "$a"; done
cd ..

cd confused_animation
for a in *.png; do convert -modulate 5,5,100 "$a" "$a"; done
cd ..

cd eye-roll_animation
for a in *.png; do convert -modulate 5,5,100 "$a" "$a"; done
cd ..

cd intro_animation
for a in *.png; do convert -modulate 5,5,100 "$a" "$a"; done
cd ..

cd look-left_animation
for a in *.png; do convert -modulate 5,5,100 "$a" "$a"; done
cd ..

cd look-right_animation
for a in *.png; do convert -modulate 5,5,100 "$a" "$a"; done
cd ..

cd look-up_animation
for a in *.png; do convert -modulate 5,5,100 "$a" "$a"; done
cd ..

cd memory_faces
for a in *.png; do convert -modulate 5,5,100 "$a" "$a"; done
cd ..

cd thinking_animation
for a in *.png; do convert -modulate 5,5,100 "$a" "$a"; done
cd ..

