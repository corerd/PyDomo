Python Imaging Libraries
========================

Performance comparison between PIL and OpenCV
---------------------------------------------
Lubuntu 16.04 (64 bit) LTS on iMac (21.5-inch, Mid 2011) using VirtualBox
```
PIL stats:
Read 324 640x480 pictures in 1.089281 seconds
deltat min: 0.002816s
deltat max: 0.004485s
deltat average 0.003362s:
```

```
OpenCV stats:
Read 324 640x480 pictures in 0.225614 seconds
deltat min: 0.000619s
deltat max: 0.001173s
deltat average 0.000696s:
```

Raspberry Pi 1 Model B+ running Arch Linux ARM
```
PIL stats:
Read 500 640x480 pictures in 43.342038 seconds
deltat min: 0.084988s
deltat max: 0.178933s
deltat average 0.086684s:
```

```
OpenCV stats:
Read 500 640x480 pictures in 10.079133 seconds
deltat min: 0.019804s
deltat max: 0.039678s
deltat average 0.020158s:
```
