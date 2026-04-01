# Pot Equations Documentation

## Equation Format
The equations are represented in the format `r(z, theta)`, where:
- **r**: Represents the radius as a function of two parameters  
- **z**: Represents the vertical position  
- **theta**: Represents the angle in radians  

## Available Functions
Here are the available functions that can be used in the equations:
- **sin(theta)**: Sine of the angle in radians.
- **cos(theta)**: Cosine of the angle in radians.
- **tan(theta)**: Tangent of the angle in radians.
- **exp(z)**: Exponential function. 
- **log(z)**: Natural logarithm of `z`.

## Example Equations
- **Basic Cylinder**:  
  `r(z, theta) = 1`
  - This represents a cylinder with a radius of 1.

- **Cone**:  
  `r(z, theta) = (1 - z/h) * R`
  - Where `R` is the base radius and `h` is the height of the cone.

- **Sphere**:  
  `r(z, theta) = sqrt(R^2 - z^2)`
  - Where `R` is the radius of the sphere.

## Reference to Google Sheets
For a complete list of available equations, refer to the following Google Sheets: [Available Equations](insert-link-here)

---

This document aims to provide a comprehensive understanding of the equation format and the functions that can be used within it. 
