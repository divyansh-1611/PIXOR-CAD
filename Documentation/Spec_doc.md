# SOFTWARE SPECIFICATION REQUIREMENTS 

## Simple 2D CAD Software 

### Introduction 

This project aims to bring the power and precision of CAD to a wider audience, making it accessible and easy to use for everyone. Our software will be designed with simplicity and user- friendliness in mind, ensuring that even those with minimal technical knowledge can create and manipulate 2D designs with ease. It will include basic features such as drawing lines, circles, rectangles, and other shapes, as well as more advanced functionalities like layer management, dimensioning, and exporting to various file formats. We believe that this project has the potential to revolutionize the way people approach design, by breaking down the barriers of traditional CAD software and making design a more inclusive & accessible field.  

---

### Requirement Analysis  

The requirement analysis for this project involves a comprehensive examination of the proposed Simple 2D CAD (Computer-Aided Design) Software. The primary goal is to ensure accessibility and ease of use for a specific user base, irrespective of their technical expertise. The software's underlying mission is to emulate the realm of design, establishing a user-friendly platform where individuals can effortlessly create and manipulate 2D designs. 

This software aims to target a wide range of audiences. It's perfect for: 

- **Students** learning about design or engineering, who need a simple tool to create and understand 2D designs. 
- **Educators**  in the field of design or engineering, who can use this tool to demonstrate concepts in a more interactive and engaging way. 
- **Hobbyists** who can use this tool to plan and visualize their projects 

Essentially, anyone who needs a user-friendly and accessible tool for creating, viewing, and manipulating  2D  designs  could  benefit from this project.  It's all  about making  design more inclusive and accessible!  

#### Success Metrics 

Some success metrics that are defined to evaluate the effectiveness of the software are: 

1. User activity - measuring the number of users actively using the software. 
1. Error rates - tracking the number of errors faced by the end user. 
1. Feature usage – monitoring the features used and demanded by the targeted userbase. 
1. User satisfaction - gathering the feedback on user satisfaction and suggestions for improvements. 

---

### Functional Specifications 

#### Core Feature Set

1. The software must include basic 2D drawing tools. These include the ability to draw straight lines, for example the user should be able to initialize a starting point for a line and the endpoint of the line. The software must also include the ability to draw circles by defining the center and radius or diameter. It should be able to add polygons as well as text labels.  
1. Another feature that the software need is to basic editing features. The end user must be able to select existing objects and move them to a new location by dragging. Implementing a copy tool that enables us to create duplicates of the objects. The software should also allow the user to delete an object. 
1. The software should create a visible grid overlay on the drawing canvas. Users should be able to toggle the grid on and off. Ensure that objects align with the grid when drawn or moved. 
1. The liberty to export created designs to SVG/JPEG/PDF formats would allow user to freely export designs in his desired format. We’ll also work on an option to import designs from these supported file formats for simplified project management. 

#### Scope Integration 

The proposed Software is completely self-contained and independent, this means it would be designed to operate independently of other systems or software. It would have all the necessary components and functionalities built-in, and wouldn’t require additional software to function. However, being self-contained might limit the software’s flexibility and scalability. For instance, users might not be able to use it alongside other tools they are familiar with, or extend its functionality through plugins or APIs. Therefore, further work needs to be done to Research the need for the same. 

---

### External Interface Specification 

It should be simple and easy for users to understand and work on. It should also be an immersive interface. For the various functions, keyboard shortcuts should be created for easier and faster implementation of various tools. On startup of our software, the device should prompt the recently accessed or created files to the user. It should also prompt an option to create a new file. Primary mode of interaction with our software would be through Mouse button trigger actions.  

---

### Technical Specification 

The primary Programming language that this software would be built on is going to be python. The specifications and versions of the libraries that we’re going to use for building this software are specified below -   

- Python Version 3.9.4 (https://www.python.org/downloads/release/python-394/) 
- Tkinter nixpkgs stable 22.11 version 3.10.11 
- Seaborn Version 0.11.2 (as this software deals with more complex visuals, Seaborn is the most suitable library for visualizations. (https://pypi.org/project/seaborn/0.11.2/)) 
- Scipy (for dealing with complex coordinate related functions to ensure smooth experience while designing.) 
- Pytest version 7.4.2 (https://pypi.org/project/pytest/) 


