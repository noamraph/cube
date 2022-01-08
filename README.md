# Simple Rubik's cube simulator

I'm pretty proud of the simplicity of the implementation. The state is stored as a dict mapping (x, y, z) coordinates to colors. The coordinates are of the imaginary cubelet outside the face - for example, the upper face of the front-top-right cubelet is `state[1, -1, 2]`. So moves are done by just applying rotations to the indices.

Press r,l,u,d,f,b to turn clockwise. Use the shift key to turn counter-clockwise. Use x,y,z to turn the entire cube.

![cube2](https://user-images.githubusercontent.com/1553464/148661029-7731a41e-1b2e-4436-9151-9bc621731aa3.gif)

