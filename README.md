# Shockwave Slicer (generalized conical slicing)

3D printers extrude plastic to build objects, and current slicers (Eg Prusa, Cura) do
so via moving the toolhead in an X-Y horizontal plane called a "slice". These 2D
slices have some issues, namely shallow angles and overhangs. If you want to print a
shape like the letter "T" the ends of the top arm will droop as the printer is
extruding plastic over nothing but air. To combat this, most slicers allow you to
generate support material to hold these parts up.

There is another option that recently emerged called "conical slicig", whereby
the "slice" is no longer flat, but instead shaped like a cone. This means
that the part grows from the inside to the outside (on the vertical axis), 
meaning that printing is much less likely to happen completely unsupported. 

The question is how to implement this generically so that it can be done on any
3D model with overhangs in any direction. This repository holds the answer.

Here's a model with some 90 degree overhangs:

![A model shaped like a question mark](documents/demo_model.png)

And here's a potential arrangement of layers that avoids needing any support
 material:

![A model shaped like a question mark with slice planes](documents/demo_layers.png)

# How does this work?

1. Given a model to print (red) An already printed part (green) And the previosly printed layer (blue)  
![Step1](documents/step1.png)

2. Displace the previously printed layer by the layer height along it’s surface normals  
![Step2](documents/step2.png)

3. Minkowski Sum with a cone of your hotends “safe” angle. (ie extrude all loose edges down and at an angle. It's pretty much the same thing.)  
![Step3](documents/step3.png)

4. Clamp to model bounds and subtract already printed parts. The result is the volume that you have to fill with plastic  
![Step4](documents/step4.png)

5. Take the top surface. This is the "slice" that the tip of the extruder travels along.  
![Step5](documents/step5.png)


How well does it work? Here's the complete shape sliced:  
![A model shaped like a question mark with slice planes](documents/demo_layers.png)

And even if there are overhangs on multiple axis it indeed does conical slices properly:  
![A model with overhangs on both X and Y axis sliced into layers](documents/demo_layers2.png)


# Current State

- Demo made in blender geometry nodes to visualize proof of concept:
    - Seems to work OK. 
    - Has issues with really thin layers as it tries to get the top surface exactly in line with the model. 
        - And other sub-layer details. Any top surface becomes part of a print plane.
    - Some minor geometry issues in this implementation (blender geometry nodes)
    - Really slow due to lots of geometry boolean operations
    - Layer lines everywhere - on the top etc
    - The same layer can be at vastly different heights – possible collisions - particularly if multiple bed contact points and horizontal overhang 

- Patent search. Haven't found anything yet. US10005126B2 doesn't cover it as we aren't using the top surface of the model to influence extrusion amounts. 

- Things I want to do:
    - Do a complete MVP: take the output of these layers, generate perimeters/contours, generate G-code toolpath, print it.
    - Get it into current open source slicing software.
    - Technical TODO's if everything goes well:
        - Find a faster implementation. It feels like there is possibly a non-iterative approach using voroni to determine print “slice” normal? Or some sort of fluid wave-propagation stuff.?
        - Reconvergence at different layer heights if multiple points on print bed. Possibly look at the min-max height of the layers and use that to determine
        what parts need more material on this layer? I'll need to diagram this at some point.


# Why "Shockwave"?
I call it "shockwave" because when drawing diagrams to figure this out I noticed
how the layers look like wave propagation:  
![hand-drawn sketch of layers](documents/shockwave.png)

It looks like someone has applied an impact to the bed and are modeling the way the
impact flows through the part to print!