# Installation
This is how I installed it on Mac OS X. If you manage to install openCV on other systems, 
please document it and do a pull request.

For Mac you need the brilliant [homebrew](https://brew.sh/) package installer. You might need XQuartz, but I'm not sure. 
It's on my system and I haven't tried uninstalling it.
```
brew reinstall opencv3 --with-python3 --c++11 --with-contrib --without-python --with-qt --with-tbb --with-opengl
brew install opencv3 --with-contrib --c++11 --with-python3 --without-python --with-qt --with-tbb --with-opengl
brew link --force opencv3
https://github.com/Polyconseil/zbarlight/
```


`--c++11` is a for modern compiler. Limited speed improvements.

`--with-qt` is a UI and window manager. Needed for openGL

`--with-tbb` is for multithreading. Speeds up the process a lot.

`--with-opengl` Speeds up the video preview a LOT! Code works without opengl, but at 8-10 fps... 

And then of course `git clone` this repository.

On the brick you need numpy:
`apt-get install python-pip python-dev python-numpy`
or
`apt-get install python-numpy`
... and a lot of patience.

# Running
- Print the templates and stick them on robots
- Plug in a webcam into your Mac/Pc and run the position_server_triangles.py
- Run the robot scripts on the robot and put the robots under the webcam
 
# Testing
The repository includes a bare server with dummy data and a bare client for your testing convenience.